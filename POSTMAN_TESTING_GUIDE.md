# 📮 Postman Testing Guide - Secure Chat App

Base URL: `https://secure-chat-app-pp81.onrender.com`

---

## 🔥 ENCRYPTED MESSAGE DEMO (Most Important for Faculty)

### Endpoint: POST /secure_message

**URL:** `https://secure-chat-app-pp81.onrender.com/secure_message`

**Method:** POST

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "user_message": "This is a secret message that will be encrypted with AES-256!"
}
```

**Response (Encrypted with AES-256-CBC):**
```json
{
  "reply": "gAAAAABmXYZ1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7A8B9C0D1E2F3G4H5I6J7K8L9M0N1O2P3Q4R5S6T7U8V9W0X1Y2Z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9A0B1C2D3E4F5G6H7I8J9K0L1M2N3O4P5Q6R7S8T9U0V1W2X3Y4Z5",
  "encrypted": true,
  "security_note": "Response encrypted with AES-256-CBC"
}
```

**What This Shows:**
- ✅ Original message is encrypted using AES-256-CBC
- ✅ Encrypted data is base64 encoded
- ✅ Cannot be decrypted without the secret key
- ✅ Demonstrates end-to-end encryption capability

---

## Other Important Endpoints

### 1. Health Check
**GET** `https://secure-chat-app-pp81.onrender.com/`

### 2. Security Status
**GET** `https://secure-chat-app-pp81.onrender.com/security/status`

### 3. User Signup
**POST** `https://secure-chat-app-pp81.onrender.com/signup`
```json
{
  "email": "demo@example.com",
  "password": "SecurePass123!"
}
```

### 4. User Login
**POST** `https://secure-chat-app-pp81.onrender.com/login`
```json
{
  "email": "demo@example.com",
  "password": "SecurePass123!"
}
```

### 5. Create Chat Session
**POST** `https://secure-chat-app-pp81.onrender.com/create_session`

### 6. Generate QR Code
**POST** `https://secure-chat-app-pp81.onrender.com/qr/create`

---

## 🎯 Quick Demo Steps for Faculty

1. **Show Security Status:**
   - GET `/security/status` → Shows ML detection enabled

2. **Show Encrypted Messages:**
   - POST `/secure_message` with plain text
   - Response shows encrypted gibberish
   - Highlight: "This is AES-256 encryption in action!"

3. **Show Authentication:**
   - POST `/signup` → Create account
   - POST `/login` → Get JWT token
   - Show the JWT token structure

4. **Show Real-time Chat:**
   - Open browser at `/static/index.html`
   - Start conversation
   - Show WebSocket connection

---

## 📱 PowerShell Alternative (No Postman Needed)

```powershell
# Test Encrypted Message
$body = @{
    user_message = "This is a secret message!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "https://secure-chat-app-pp81.onrender.com/secure_message" -Method Post -Body $body -ContentType "application/json"

Write-Host "Encrypted Response:" -ForegroundColor Green
$response.reply
```

---

**The encrypted message endpoint is the best way to demonstrate AES-256 encryption in action!**
