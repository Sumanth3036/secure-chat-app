from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict
import secrets
import string
from datetime import datetime

# DB collection
from .db import qrcodes as qrcodes_collection

# Router
router = APIRouter()

# Pydantic models
class QRCodeCreate(BaseModel):
    pass  # No body needed for creation

class QRCodeStatus(BaseModel):
    token: str
    status: str

class QRCodeJoin(BaseModel):
    pass  # No body needed for joining

# Helper function to generate random token
def generate_token(length: int = 16) -> str:
    """Generate a random alphanumeric token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Endpoints
@router.post("/create", response_model=QRCodeStatus)
async def create_qr_code():
    """
    Create a new QR code with a random token.
    Returns the token and initial status.
    """
    # Generate unique token
    while True:
        token = generate_token()
        existing = await qrcodes_collection.find_one({"token": token})
        if not existing:
            break
    
    # Create QR code entry
    doc = {
        "token": token,
        "status": "waiting",
        "created_at": datetime.utcnow()
    }
    
    # Store in DB
    await qrcodes_collection.insert_one(doc)
    
    return {"token": token, "status": "waiting"}

@router.get("/{token}/status", response_model=QRCodeStatus)
async def get_qr_status(token: str):
    """
    Get the status of a QR code by token.
    """
    qr = await qrcodes_collection.find_one({"token": token})
    if not qr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )
    
    return {"token": token, "status": qr.get("status", "waiting")}

@router.post("/{token}/join", response_model=QRCodeStatus)
async def join_qr_session(token: str):
    """
    Join a QR code session by setting status to 'joined'.
    """
    qr = await qrcodes_collection.find_one({"token": token})
    if not qr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )
    
    await qrcodes_collection.update_one({"token": token}, {"$set": {"status": "joined", "joined_at": datetime.utcnow()}})
    
    return {"token": token, "status": "joined"}


