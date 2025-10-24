from fastapi import FastAPI, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response, FileResponse
from pydantic import BaseModel
from passlib.hash import bcrypt
from typing import Dict, List
from uuid import uuid4
import qrcode
import io
import jwt
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json
import re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
from dotenv import load_dotenv
from security_monitor import security_monitor, SecurityWarning
from ml_detector import get_detector

# Load environment variables
load_dotenv()

app = FastAPI(title="Secure Chat App", version="2.0.0")

# Security configuration from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "1"))

# AES encryption configuration
AES_SECRET_KEY = os.getenv("AES_SECRET_KEY", "your-32-character-aes-secret-key-here").encode()
AES_IV = os.getenv("AES_IV", "your-16-character-iv-here").encode()

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "chat_app")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "users")

# MongoDB client
mongodb_client = None
mongodb_connected = False

# In-memory fallback storage (when MongoDB is unavailable)
in_memory_users = {}
in_memory_qr_tokens = {}

# WebSocket connection manager
class RoomConnectionManager:
    def __init__(self):
        # session_id -> list[WebSocket]
        self.room_to_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.room_to_connections.setdefault(session_id, []).append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        connections = self.room_to_connections.get(session_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and session_id in self.room_to_connections:
            del self.room_to_connections[session_id]

    async def broadcast(self, session_id: str, message: dict):
        connections = list(self.room_to_connections.get(session_id, []))
        for connection in connections:
            try:
                await connection.send_json(message)
            except:
                # Remove dead connections
                try:
                    connections.remove(connection)
                except Exception:
                    pass

manager = RoomConnectionManager()

# In-memory session registry (can be moved to MongoDB later)
SESSIONS: Dict[str, dict] = {}

# Pydantic models
class UserSignup(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ChatMessage(BaseModel):
    user_message: str

class QRToken(BaseModel):
    token: str

class ValidateContent(BaseModel):
    content: str
    content_type: str = "text"  # text, url, qr

# AES Encryption/Decryption functions
def encrypt_message(message: str) -> str:
    """Encrypt a message using AES-256-CBC"""
    try:
        # Create cipher
        cipher = Cipher(
            algorithms.AES(AES_SECRET_KEY),
            modes.CBC(AES_IV),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Pad the message
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        
        # Encrypt
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return base64 encoded encrypted data
        return base64.b64encode(encrypted_data).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return message  # Fallback to plain text

def decrypt_message(encrypted_message: str) -> str:
    """Decrypt a message using AES-256-CBC"""
    try:
        # Decode base64
        encrypted_data = base64.b64decode(encrypted_message.encode())
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(AES_SECRET_KEY),
            modes.CBC(AES_IV),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        return decrypted_data.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return encrypted_message  # Fallback to encrypted text

# QR Token functions
def generate_qr_token(user_email: str) -> str:
    """Generate a one-time encrypted token for QR code"""
    try:
        # Create token data with user email and expiry
        token_data = {
            "user_email": user_email,
            "expires_at": (datetime.utcnow() + timedelta(minutes=1)).isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Convert to JSON string and encrypt
        token_json = json.dumps(token_data)
        encrypted_token = encrypt_message(token_json)
        
        return encrypted_token
    except Exception as e:
        print(f"QR token generation error: {e}")
        return ""

def validate_qr_token(encrypted_token: str) -> dict:
    """Validate and decrypt a QR token"""
    try:
        # Decrypt the token
        decrypted_json = decrypt_message(encrypted_token)
        token_data = json.loads(decrypted_json)
        
        # Check if token has expired
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if datetime.utcnow() > expires_at:
            return {"valid": False, "error": "Token expired"}
        
        return {
            "valid": True,
            "user_email": token_data["user_email"],
            "created_at": token_data["created_at"]
        }
    except Exception as e:
        print(f"QR token validation error: {e}")
        return {"valid": False, "error": "Invalid token"}

# MongoDB utility functions
async def connect_to_mongo():
    global mongodb_client
    # Add timeout settings to prevent hanging
    mongodb_client = AsyncIOMotorClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=5000,  # 5 seconds timeout
        connectTimeoutMS=5000,
        socketTimeoutMS=5000
    )
    # Test the connection
    await mongodb_client.admin.command('ping')
    print(f"Connected to MongoDB at {MONGODB_URL}")

async def close_mongo_connection():
    global mongodb_client
    if mongodb_client is not None:
        mongodb_client.close()
        print("MongoDB connection closed")

def get_user_collection():
    if mongodb_client is None:
        raise RuntimeError("MongoDB not connected")
    return mongodb_client[DATABASE_NAME][COLLECTION_NAME]

def get_qr_tokens_collection():
    if mongodb_client is None:
        raise RuntimeError("MongoDB not connected")
    return mongodb_client[DATABASE_NAME]["qr_tokens"]

# JWT utility functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    global mongodb_connected, mongodb_client
    try:
        await connect_to_mongo()
        
        # Only create indexes if MongoDB is actually connected
        if mongodb_client is not None:
            user_collection = get_user_collection()
            qr_tokens_collection = get_qr_tokens_collection()
            
            # Ensure unique email index for users
            await user_collection.create_index("email", unique=True)
            
            # Ensure unique token index for QR tokens and TTL index for expiry
            await qr_tokens_collection.create_index("token", unique=True)
            await qr_tokens_collection.create_index("expires_at", expireAfterSeconds=0)  # TTL index
            
            mongodb_connected = True
            print("✅ MongoDB connected successfully")
        else:
            raise Exception("MongoDB client is None")
    except Exception as e:
        mongodb_connected = False
        mongodb_client = None  # Ensure client is None
        print(f"⚠️  MongoDB connection failed: {str(e)[:100]}")
        print("⚠️  Using in-memory storage (data will not persist)")
    
    print("\n🔐 Security features enabled:")
    print(f"   - Storage: {'MongoDB' if mongodb_connected else 'In-Memory (temporary)'}")
    print(f"   - JWT Algorithm: {ALGORITHM}")
    print(f"   - Token Expiry: {ACCESS_TOKEN_EXPIRE_HOURS} hours")
    print(f"   - AES Encryption: {'Enabled' if len(AES_SECRET_KEY) == 32 else 'Warning: Key length incorrect'}")
    print(f"   - Password Hashing: bcrypt enabled")
    print(f"   - QR Token Security: AES encrypted + 1-minute expiry")
    print(f"\n🚀 Server is running at http://localhost:8000")
    print(f"📱 Access the app at http://localhost:8000/static/index.html\n")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files - use absolute path for deployment compatibility
CLIENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "client")
app.mount("/static", StaticFiles(directory=CLIENT_DIR), name="static")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Secure Chat Server Running", "security": "AES-256 + bcrypt + JWT enabled"}

# Favicon endpoint to prevent 404 errors
@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)  # No Content - silently ignore favicon requests

# QR Validation page
@app.get("/qr-validate")
async def qr_validate_page():
    return FileResponse(os.path.join(CLIENT_DIR, "qr_validate.html"))

# Signup endpoint with enhanced bcrypt security
@app.post("/signup")
async def signup(user: UserSignup):
    # Enhanced password validation
    if len(user.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Check for special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(char in special_chars for char in user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
        )
    
    # Hash password with bcrypt
    hashed_password = bcrypt.hash(user.password, rounds=12)
    
    user_doc = {
        "email": user.email,
        "password_hash": hashed_password,
        "created_at": datetime.utcnow(),
        "security_level": "bcrypt-12-rounds"
    }
    
    # Use MongoDB if connected, otherwise use in-memory storage
    if mongodb_connected:
        try:
            user_collection = get_user_collection()
            
            # Check if user already exists
            existing_user = await user_collection.find_one({"email": user.email})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists"
                )
            
            # Insert user into MongoDB
            await user_collection.insert_one(user_doc)
        except HTTPException:
            raise  # Re-raise HTTPException as-is
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
    else:
        # Use in-memory storage
        if user.email in in_memory_users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        in_memory_users[user.email] = user_doc
    
    return {"message": "User registered successfully with enhanced security"}

# Login endpoint with bcrypt verification
@app.post("/login")
async def login(user: UserLogin):
    db_user = None
    
    # Use MongoDB if connected, otherwise use in-memory storage
    if mongodb_connected:
        try:
            user_collection = get_user_collection()
            db_user = await user_collection.find_one({"email": user.email})
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
    else:
        # Use in-memory storage
        db_user = in_memory_users.get(user.email)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password with bcrypt
    if not bcrypt.verify(user.password, db_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate JWT token
    token_data = {"sub": user.email}
    access_token = create_access_token(data=token_data)
    
    return {
        "message": "Login successful",
        "token": access_token,
        "security_info": "Password verified with bcrypt, JWT token generated"
    }

# Enhanced chat endpoint with encryption
@app.post("/chat")
async def chat(message: ChatMessage):
    # Encrypt the response message
    response_text = f"This is a secure response for: {message.user_message}"
    encrypted_response = encrypt_message(response_text)
    
    return {
        "reply": encrypted_response,
        "encrypted": True,
        "security_note": "Response encrypted with AES-256-CBC"
    }

# Secure QR Code endpoint with encrypted tokens
@app.get("/generate_qr")
async def generate_qrcode(user_email: str = Query(..., description="User email for QR code")):
    try:
        # Generate encrypted token
        encrypted_token = generate_qr_token(user_email)
        if not encrypted_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate QR token"
            )
        
        # Store token in MongoDB or in-memory
        if mongodb_connected:
            qr_tokens_collection = get_qr_tokens_collection()
            token_doc = {
                "token": encrypted_token,
                "user_email": user_email,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=1),
                "used": False
            }
            await qr_tokens_collection.insert_one(token_doc)
        else:
            # Store in memory
            in_memory_qr_tokens[encrypted_token] = {
                "user_email": user_email,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=1),
                "used": False
            }
        
        # Generate QR code with encrypted token (not raw email)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(encrypted_token)  # Encrypted token instead of raw email
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return Response(content=img_buffer.getvalue(), media_type="image/png")
        
    except Exception as e:
        print(f"QR generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate QR code"
        )

# QR Token validation endpoint
@app.post("/validate_qr")
async def validate_qr_token_endpoint(qr_token: QRToken):
    try:
        # Validate the encrypted token
        validation_result = validate_qr_token(qr_token.token)
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_result["error"]
            )
        
        # Check if token exists and hasn't been used
        if mongodb_connected:
            qr_tokens_collection = get_qr_tokens_collection()
            token_doc = await qr_tokens_collection.find_one({
                "token": qr_token.token,
                "used": False
            })
            
            if not token_doc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token not found or already used"
                )
            
            # Mark token as used
            await qr_tokens_collection.update_one(
                {"token": qr_token.token},
                {"$set": {"used": True, "used_at": datetime.utcnow()}}
            )
        else:
            # Check in-memory storage
            token_doc = in_memory_qr_tokens.get(qr_token.token)
            if not token_doc or token_doc.get("used"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token not found or already used"
                )
            
            # Mark as used
            in_memory_qr_tokens[qr_token.token]["used"] = True
            in_memory_qr_tokens[qr_token.token]["used_at"] = datetime.utcnow()
        
        # Generate JWT token for the user
        user_email = validation_result["user_email"]
        token_data = {"sub": user_email}
        access_token = create_access_token(data=token_data)
        
        return {
            "message": "QR token validated successfully",
            "token": access_token,
            "user_email": user_email,
            "security_info": "QR token validated, JWT generated, token marked as used"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"QR validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate QR token"
        )

# New: Create private session and room-based WebSocket
class CreateSessionResponse(BaseModel):
    session_id: str
    join_url: str

@app.post("/create_session", response_model=CreateSessionResponse)
async def create_session():
    session_id = uuid4().hex
    SESSIONS[session_id] = {
        "created_at": datetime.utcnow().isoformat()
    }
    # Construct a join URL pointing to the chat client with session_id
    join_url = f"/static/chat.html?session_id={session_id}"
    return {"session_id": session_id, "join_url": join_url}

@app.get("/qr_from_session/{session_id}")
async def qr_from_session(session_id: str):
    # Validate session exists
    if session_id not in SESSIONS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    # Encode a full join URL for sharing (client will request relative path)
    join_url = f"/static/chat.html?session_id={session_id}"
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(join_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        return Response(content=img_buffer.getvalue(), media_type="image/png")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate QR code")

@app.websocket("/ws/{session_id}")
async def websocket_room_endpoint(websocket: WebSocket, session_id: str, token: str = Query(...)):
    # Verify JWT token
    user_email = verify_token(token)
    if not user_email:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    # Validate session
    if session_id not in SESSIONS:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(session_id, websocket)
    try:
        welcome_msg = f"Welcome {user_email}! Joined session {session_id}."
        encrypted_welcome = encrypt_message(welcome_msg)
        await websocket.send_json({
            "user": "System",
            "message": encrypted_welcome,
            "encrypted": True,
            "security_info": "Message encrypted with AES-256-CBC"
        })

        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                user = message_data.get("user", user_email)
                message = message_data.get("message", "")
                
                # Check if message contains URLs - perform ML analysis
                urls = re.findall(r'https?://[^\s]+', message)
                ml_threat_info = None
                
                if urls:
                    try:
                        # Get ML detector and analyze URLs
                        ml_detector = get_detector()
                        if ml_detector:
                            phishing_prob = ml_detector.predict_proba(message)
                            if phishing_prob is not None:
                                # Determine threat level
                                if phishing_prob > 0.7:
                                    threat_level = "dangerous"
                                    threat_color = "#dc3545"  # Red
                                    threat_emoji = "🔴"
                                elif phishing_prob > 0.4:
                                    threat_level = "warning"
                                    threat_color = "#ffc107"  # Yellow
                                    threat_emoji = "🟡"
                                else:
                                    threat_level = "safe"
                                    threat_color = "#28a745"  # Green
                                    threat_emoji = "🟢"
                                
                                ml_threat_info = {
                                    "level": threat_level,
                                    "color": threat_color,
                                    "emoji": threat_emoji,
                                    "probability": float(phishing_prob),
                                    "confidence": f"{phishing_prob*100:.1f}%"
                                }
                    except Exception as e:
                        print(f"ML URL analysis error: {e}")
                
                # Security monitoring - analyze message for threats
                warnings = security_monitor.analyze_message(user_email, session_id, message)
                
                # Add warnings to user's record
                for warning in warnings:
                    security_monitor.add_warning(warning)
                
                # Check if session should be terminated
                if security_monitor.should_terminate_session(user_email, session_id):
                    termination_msg = "Session terminated due to security violations."
                    encrypted_termination = encrypt_message(termination_msg)
                    await websocket.send_json({
                        "user": "Security System",
                        "message": encrypted_termination,
                        "encrypted": True,
                        "security_info": "Session terminated due to multiple security warnings",
                        "terminated": True
                    })
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return
                
                # Send warning messages if any
                for warning in warnings:
                    warning_msg = f"Security Warning: {warning.message}"
                    encrypted_warning = encrypt_message(warning_msg)
                    await websocket.send_json({
                        "user": "Security System",
                        "message": encrypted_warning,
                        "encrypted": True,
                        "security_info": f"Warning {security_monitor.get_warning_count(user_email, session_id)}/{security_monitor.max_warnings_before_ban}",
                        "warning": True
                    })
                
                encrypted_message = encrypt_message(message)
                response = {
                    "user": user,
                    "message": encrypted_message,
                    "encrypted": True,
                    "timestamp": datetime.utcnow().isoformat(),
                    "security_info": "Message encrypted with AES-256-CBC"
                }
                
                # Add ML threat info if URLs were detected
                if ml_threat_info:
                    response["ml_threat"] = ml_threat_info
                
                await manager.broadcast(session_id, response)
            except json.JSONDecodeError:
                error_msg = "Invalid message format. Please send JSON with 'user' and 'message' fields."
                encrypted_error = encrypt_message(error_msg)
                await websocket.send_json({
                    "user": "System",
                    "message": encrypted_error,
                    "encrypted": True,
                    "error": True
                })
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)

# Security monitoring endpoints
@app.get("/security/report/{session_id}")
async def get_security_report(session_id: str, token: str = Query(...)):
    """Get security report for a session (requires authentication)"""
    user_email = verify_token(token)
    if not user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    if session_id not in SESSIONS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    return security_monitor.get_security_report(user_email, session_id)

@app.post("/security/clear_warnings/{session_id}")
async def clear_warnings(session_id: str, token: str = Query(...)):
    """Clear warnings for a user in a session (requires authentication)"""
    user_email = verify_token(token)
    if not user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    if session_id not in SESSIONS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    security_monitor.clear_warnings(user_email, session_id)
    return {"message": "Warnings cleared successfully"}

# ML-powered validation endpoint
@app.post("/api/validate")
async def validate_content(content: ValidateContent):
    """Validate content using ML model and rule-based detection"""
    try:
        # Get ML detector
        ml_detector = get_detector()
        
        # Extract URLs from content
        urls = re.findall(r'https?://[^\s]+', content.content)
        
        # Initialize response
        warnings = []
        ml_detection = {
            "enabled": ml_detector is not None and not ml_detector.fallback_mode,
            "phishing_probability": 0.0,
            "risk_level": "low",
            "model_type": "CatBoost Classifier" if ml_detector and not ml_detector.fallback_mode else "Rule-based"
        }
        
        # ML Detection
        if ml_detector:
            try:
                phishing_prob = ml_detector.predict_proba(content.content)
                if phishing_prob is not None:
                    ml_detection["phishing_probability"] = float(phishing_prob)
                    
                    # Determine risk level
                    if phishing_prob > 0.7:
                        ml_detection["risk_level"] = "high"
                        warnings.append({
                            "type": "ml_phishing_detection",
                            "message": f"ML model detected potential phishing (confidence: {phishing_prob*100:.2f}%)",
                            "severity": "critical",
                            "timestamp": datetime.utcnow().isoformat(),
                            "source": "catboost_ml_model"
                        })
                    elif phishing_prob > 0.4:
                        ml_detection["risk_level"] = "medium"
                        warnings.append({
                            "type": "ml_phishing_detection",
                            "message": f"ML model detected suspicious content (confidence: {phishing_prob*100:.2f}%)",
                            "severity": "high",
                            "timestamp": datetime.utcnow().isoformat(),
                            "source": "catboost_ml_model"
                        })
                    else:
                        ml_detection["risk_level"] = "low"
            except Exception as e:
                print(f"ML detection error: {e}")
        
        # Rule-based detection using security monitor
        security_warnings = security_monitor.analyze_message(
            user_email="validation_api",
            session_id="api_validation",
            message=content.content
        )
        
        # Convert security warnings to response format
        for warning in security_warnings:
            warnings.append({
                "type": warning.warning_type,
                "message": warning.message,
                "severity": warning.severity,
                "timestamp": warning.timestamp.isoformat(),
                "source": "rule_based_detection"
            })
        
        # Determine overall status
        is_safe = len(warnings) == 0
        if ml_detection["risk_level"] == "high" or any(w["severity"] == "critical" for w in warnings):
            status = "dangerous"
            is_safe = False
        elif ml_detection["risk_level"] == "medium" or any(w["severity"] in ["high", "medium"] for w in warnings):
            status = "warning"
            is_safe = False
        else:
            status = "safe"
        
        # Build response
        response = {
            "is_safe": is_safe,
            "status": status,
            "warnings": warnings,
            "details": {
                "ml_detection": ml_detection,
                "rule_based_detection": {
                    "warnings_count": len(security_warnings),
                    "enabled": True
                },
                "content_type": content.content_type,
                "content_length": len(content.content),
                "urls_found": len(urls),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return response
        
    except Exception as e:
        print(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )

# Security status endpoint
@app.get("/security/status")
async def security_status():
    # Get ML detector status
    ml_detector = get_detector()
    ml_enabled = ml_detector is not None and not ml_detector.fallback_mode
    
    return {
        "jwt_enabled": True,
        "bcrypt_enabled": True,
        "aes_encryption": True,
        "password_rounds": 12,
        "encryption_algorithm": "AES-256-CBC",
        "qr_token_security": {
            "encryption": "AES-256-CBC",
            "expiry": "1 minute",
            "storage": "MongoDB with TTL" if mongodb_connected else "In-Memory",
            "one_time_use": True,
            "no_raw_data": True
        },
        "security_monitoring": {
            "enabled": True,
            "phishing_detection": True,
            "malicious_content_detection": True,
            "spam_detection": True,
            "rate_limiting": True,
            "max_warnings_before_ban": 3,
            "max_messages_per_minute": 30
        },
        "ml_phishing_detection": {
            "enabled": ml_enabled,
            "model_type": "CatBoost Classifier" if ml_enabled else "Rule-based Fallback",
            "model_accuracy": "96.79%" if ml_enabled else "N/A",
            "features_count": 30,
            "fallback_mode": ml_detector.fallback_mode if ml_detector else True,
            "model_path": ml_detector.model_path if ml_detector else "N/A"
        },
        "security_level": "Enhanced with ML + Rule-Based Detection" if ml_enabled else "Enhanced with Security Monitoring"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
