from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
from datetime import timedelta

# Router
router = APIRouter()

# Mock models
class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

MOCK_TOKEN = "mock-token"

@router.post("/register")
async def register(_: UserRegister):
    return {"msg": "registered (mock)", "token": MOCK_TOKEN}

@router.post("/login")
async def login(_: UserLogin):
    return {"msg": "logged in (mock)", "token": MOCK_TOKEN}

@router.get("/me")
async def me():
    return {"email": "mock@example.com"}

# OAuth stubs
@router.get("/google/login")
async def google_login(_: Request):
    return {"msg": "google oauth not configured (mock)"}

@router.get("/google/callback")
async def google_callback(_: Request):
    return {"msg": "google oauth callback (mock)", "token": MOCK_TOKEN}

@router.get("/facebook/login")
async def facebook_login(_: Request):
    return {"msg": "facebook oauth not configured (mock)"}

@router.get("/facebook/callback")
async def facebook_callback(_: Request):
    return {"msg": "facebook oauth callback (mock)", "token": MOCK_TOKEN}
