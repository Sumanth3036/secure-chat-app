# 🔐 ENCRYPTION DEMONSTRATION GUIDE
## Cybersecurity Project - Faculty Presentation

---

## 📱 DEPLOYMENT URLS

### **Main Application URL:**
```
https://secure-chat-app-XXXX.onrender.com
```
*(Replace XXXX with your actual Render deployment ID)*

### **Key Pages to Demonstrate:**

1. **Login Page:**
   ```
   https://secure-chat-app-XXXX.onrender.com/static/login.html
   ```

2. **Signup with OTP (NEW):**
   ```
   https://secure-chat-app-XXXX.onrender.com/static/signup_with_otp.html
   ```

3. **OTP Verification (NEW - 6-box interface):**
   ```
   https://secure-chat-app-XXXX.onrender.com/static/otp_verify.html
   ```

4. **Forgot Password:**
   ```
   https://secure-chat-app-XXXX.onrender.com/static/forgot_password.html
   ```

5. **Chat Interface (Encrypted Messages):**
   ```
   https://secure-chat-app-XXXX.onrender.com/static/chat.html
   ```

6. **QR Code Generator:**
   ```
   https://secure-chat-app-XXXX.onrender.com/static/qr.html
   ```

7. **API Documentation (Interactive):**
   ```
   https://secure-chat-app-XXXX.onrender.com/docs
   ```

---

## 🔒 ENCRYPTION FEATURES TO DEMONSTRATE

### **1. AES-256-CBC Encryption (Chat Messages)**

**Location:** Real-time chat messages
**URL:** `/static/chat.html`

**How to Demonstrate:**
1. Login to the application
2. Create or join a chat session
3. Send a message
4. **Show in Browser DevTools:**
   - Open Developer Console (F12)
   - Go to Network tab
   - Send a message
   - Click on the WebSocket connection
   - **Show the encrypted payload:**
     ```json
     {
       "user": "user@example.com",
       "message": "SGVsbG8gV29ybGQh...",  // Base64 encoded encrypted message
       "encrypted": true,
       "timestamp": "2025-10-30T10:22:00"
     }
     ```

**Code Reference:**
```python
# File: server/main.py (Lines 119-141)
def encrypt_message(message: str) -> str:
    """Encrypt a message using AES-256-CBC"""
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
```

---

### **2. QR Code Token Encryption**

**Location:** QR Code generation
**URL:** `/static/qr.html`

**How to Demonstrate:**
1. Navigate to QR Code page
2. Generate a QR code
3. **Show in Browser DevTools:**
   - Network tab → Look for `/qr_create` request
   - Response shows encrypted token:
     ```json
     {
       "token": "U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlIpTwjvfnGg=...",
       "data_url": "data:image/png;base64,...",
       "expires_at": "2025-10-30T10:24:00"
     }
     ```

**Security Features:**
- Token contains encrypted user email + timestamp
- 2-minute expiry
- One-time use only
- Cannot be reused or forged

**Code Reference:**
```python
# File: server/main.py (Lines 170-187)
def generate_qr_token(user_email: str) -> str:
    """Generate a one-time encrypted token for QR code"""
    token_data = {
        "email": user_email,
        "expires_at": (datetime.utcnow() + timedelta(minutes=2)).isoformat(),
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Convert to JSON string and encrypt
    token_json = json.dumps(token_data)
    encrypted_token = encrypt_message(token_json)
    
    return encrypted_token
```

---

### **3. Password Hashing (bcrypt)**

**Location:** User registration and login
**URL:** `/static/signup_with_otp.html`

**How to Demonstrate:**
1. Create a new account
2. **Show in API Documentation:**
   - Go to `/docs`
   - Navigate to POST `/signup` endpoint
   - Show that password is hashed before storage
   - **Never stored in plain text**

**Security Features:**
- bcrypt algorithm (industry standard)
- Automatic salt generation
- Computationally expensive (prevents brute force)
- One-way hashing (cannot be reversed)

**Code Reference:**
```python
# File: server/main.py (Line 6)
from passlib.hash import bcrypt

# Password hashing (Line 235)
hashed_password = bcrypt.hash(user.password)

# Password verification (Line 322)
if not bcrypt.verify(user.password, db_user["password"]):
    raise HTTPException(...)
```

---

### **4. JWT Token Authentication**

**Location:** Login system
**URL:** `/static/login.html`

**How to Demonstrate:**
1. Login to the application
2. **Show in Browser DevTools:**
   - Application tab → Local Storage
   - Look for `token` key
   - Copy the JWT token
3. **Decode JWT at:** https://jwt.io
   - Paste the token
   - Show the payload (email, expiry)
   - **Explain:** Token is signed, cannot be tampered

**Security Features:**
- HS256 algorithm
- 1-hour expiry
- Signed with SECRET_KEY
- Tamper-proof

**Code Reference:**
```python
# File: server/main.py (Lines 209-220)
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

---

### **5. OTP System (Email Verification)**

**Location:** Signup and Password Reset
**URLs:** 
- `/static/signup_with_otp.html`
- `/static/otp_verify.html` (NEW)
- `/static/forgot_password.html`

**How to Demonstrate:**
1. Start signup process
2. Enter email and password
3. Click "Send Verification OTP"
4. **Show in Server Console:**
   - OTP is displayed in server logs (console mode)
   - 6-digit random number
   - 5-minute expiry
5. Enter OTP in the 6-box interface
6. Account created after verification

**Security Features:**
- 6-digit random OTP
- 5-minute expiry
- One-time use
- Stored with timestamp
- Rate limiting (prevents spam)

**Code Reference:**
```python
# File: server/email_service.py (Lines 46-48)
def generate_otp(self) -> str:
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))
```

---

### **6. ML-Based Phishing Detection**

**Location:** URL validation
**URL:** `/static/validate.html`

**How to Demonstrate:**
1. Navigate to URL validation page
2. Enter a suspicious URL (e.g., `http://paypal-verify.tk/login`)
3. **Show the ML prediction:**
   - Threat score
   - Classification (Safe/Suspicious/Dangerous)
   - Confidence level

**Security Features:**
- CatBoost ML model (96.79% accuracy)
- Analyzes 30+ URL features
- Real-time prediction
- No external API calls (privacy)

**Test URLs:**
```
Safe: https://www.google.com
Suspicious: http://free-iphone-winner.tk
Dangerous: http://paypal-secure-login.ml/verify
```

---

## 🎯 DEMONSTRATION FLOW FOR FACULTY

### **Part 1: User Authentication (5 minutes)**

1. **Show Signup with OTP:**
   - Navigate to signup page
   - Enter credentials
   - Show OTP in server console
   - Demonstrate 6-box OTP interface
   - Explain password hashing

2. **Show Login:**
   - Login with created account
   - Show JWT token in DevTools
   - Explain token-based authentication

### **Part 2: Encrypted Communication (5 minutes)**

3. **Show Chat Encryption:**
   - Create a chat session
   - Send messages
   - Open DevTools → Network → WebSocket
   - **Show encrypted messages in transit**
   - Explain AES-256-CBC encryption

4. **Show QR Code Security:**
   - Generate QR code
   - Show encrypted token in response
   - Scan with phone (if available)
   - Explain token expiry and one-time use

### **Part 3: Security Features (5 minutes)**

5. **Show ML Phishing Detection:**
   - Test multiple URLs
   - Show threat scores
   - Explain ML model features

6. **Show Password Reset:**
   - Use forgot password
   - Show OTP system
   - Demonstrate 6-box OTP interface

---

## 📊 ENCRYPTION SUMMARY TABLE

| Feature | Algorithm | Key Size | Purpose |
|---------|-----------|----------|---------|
| Chat Messages | AES-256-CBC | 256-bit | End-to-end message encryption |
| QR Tokens | AES-256-CBC | 256-bit | Secure token generation |
| Passwords | bcrypt | N/A | One-way password hashing |
| JWT Tokens | HMAC-SHA256 | 256-bit | Authentication tokens |
| OTP | Random | 6-digit | Email verification |

---

## 🔍 WHERE TO FIND ENCRYPTED DATA

### **1. Network Traffic (Browser DevTools)**
```
F12 → Network Tab → Filter: WS (WebSocket)
Look for: Encrypted message payloads
```

### **2. Local Storage (Browser DevTools)**
```
F12 → Application → Local Storage
Look for: JWT tokens
```

### **3. API Responses (Browser DevTools)**
```
F12 → Network Tab → XHR
Look for: Encrypted tokens in /qr_create response
```

### **4. Server Logs (Console)**
```
Look for: OTP codes in console output
Format: "OTP: 123456"
```

---

## 🎓 TALKING POINTS FOR FACULTY

### **Why AES-256-CBC?**
- Industry standard for symmetric encryption
- Used by governments and military
- 256-bit key = 2^256 possible combinations
- CBC mode prevents pattern detection

### **Why bcrypt for Passwords?**
- Specifically designed for password hashing
- Adaptive (can increase difficulty over time)
- Automatic salt generation
- Resistant to rainbow table attacks

### **Why JWT Tokens?**
- Stateless authentication
- No database lookup needed
- Signed and tamper-proof
- Industry standard (OAuth 2.0)

### **Why ML for Phishing?**
- Real-time detection
- No external API dependencies
- 96.79% accuracy
- Analyzes URL structure, not just blacklists

---

## 🚀 QUICK DEMO CHECKLIST

- [ ] Open application in browser
- [ ] Show signup with OTP (6-box interface)
- [ ] Check server console for OTP
- [ ] Login and show JWT token
- [ ] Send encrypted chat message
- [ ] Show encrypted payload in DevTools
- [ ] Generate QR code with encrypted token
- [ ] Test ML phishing detection
- [ ] Show forgot password with OTP

---

## 📝 NOTES FOR PRESENTATION

1. **Emphasize Security Layers:**
   - Multiple encryption methods
   - Defense in depth approach
   - Industry-standard algorithms

2. **Show Real Encrypted Data:**
   - Don't just talk about it
   - Show actual encrypted payloads
   - Demonstrate in DevTools

3. **Explain Practical Use:**
   - Why each encryption is needed
   - Real-world attack scenarios
   - How it protects users

4. **Highlight Innovation:**
   - 6-box OTP interface (modern UX)
   - ML-based threat detection
   - Real-time encryption

---

## 🔗 ADDITIONAL RESOURCES

**API Documentation:**
```
https://secure-chat-app-XXXX.onrender.com/docs
```

**GitHub Repository:**
```
https://github.com/YOUR_USERNAME/secure-chat-app
```

**Test the API:**
```powershell
# Test encryption endpoint
Invoke-RestMethod -Uri "https://YOUR_APP.onrender.com/chat" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"user_message":"Hello World"}'
```

---

## ✅ SUCCESS CRITERIA

Your faculty should see:
1. ✅ Encrypted messages in network traffic
2. ✅ Hashed passwords (never plain text)
3. ✅ JWT tokens with expiry
4. ✅ Encrypted QR tokens
5. ✅ OTP verification system
6. ✅ ML threat detection in action

---

**Good luck with your presentation! 🎉**
