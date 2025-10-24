# 🚀 START HERE - CyberProject Quick Start Guide

## ⚡ 3-Step Quick Start

### Step 1: Start MongoDB
```powershell
# Check if MongoDB is running
Get-Process mongod

# If not running, start it
mongod --dbpath "C:\data\db"
```

### Step 2: Start the Server
```powershell
# Open new terminal and run:
cd c:\Users\suman\OneDrive\Documents\cyber\cyberproject\server
python main.py
```

**Wait for this message:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Test Everything
```powershell
# Open new terminal and run:
cd c:\Users\suman\OneDrive\Documents\cyber\cyberproject
.\test_api.ps1
```

---

## 🎯 What This Project Does

This is a **Secure Chat Application** with:
- 🔐 **End-to-end encryption** (AES-256)
- 🤖 **ML-based phishing detection** (CatBoost)
- 🔒 **Secure authentication** (JWT + bcrypt)
- 💬 **Real-time chat** (WebSocket)
- 📱 **QR code sharing** (encrypted tokens)
- 🛡️ **Security monitoring** (phishing, XSS, spam)

---

## 📋 Manual Testing Commands

### Test 1: Check Server
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/" -Method GET
```

### Test 2: Create Account
```powershell
$body = @{ email = "test@example.com"; password = "Test123!@#" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/signup" -Method POST -Body $body -ContentType "application/json"
```

### Test 3: Login
```powershell
$body = @{ email = "test@example.com"; password = "Test123!@#" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/login" -Method POST -Body $body -ContentType "application/json"
```

### Test 4: Test Phishing Detection
```powershell
$body = @{ content = "Click here: http://phishing.com"; content_type = "text" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/validate" -Method POST -Body $body -ContentType "application/json"
```

---

## 🌐 Open in Browser

```powershell
# Signup page
Start-Process "http://localhost:8000/static/signup.html"

# Login page
Start-Process "http://localhost:8000/static/login.html"

# Main app
Start-Process "http://localhost:8000/static/index.html"

# Validation tool
Start-Process "http://localhost:8000/static/validate.html"
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **START_HERE.md** | This file - Quick start |
| **QUICK_TEST_COMMANDS.md** | Command reference |
| **MANUAL_TESTING_GUIDE.md** | Complete testing guide |
| **PROJECT_STATUS.md** | Full project status |
| **FUNCTIONALITY_TEST.md** | Feature testing |
| **SECURITY_FEATURES.md** | Security docs |

---

## ✅ Verification Checklist

Before testing, verify:
- [ ] MongoDB is running (`Get-Process mongod`)
- [ ] Server is running (`python main.py` in server folder)
- [ ] Server shows "Uvicorn running on http://0.0.0.0:8000"
- [ ] No error messages in server terminal

---

## 🔥 One-Command Test

```powershell
# Test if everything is working
Invoke-RestMethod "http://localhost:8000/security/status" | ConvertTo-Json
```

**Expected output:**
```json
{
  "jwt_enabled": true,
  "bcrypt_enabled": true,
  "aes_encryption": true,
  "security_level": "Enhanced with Security Monitoring"
}
```

---

## 🐛 Troubleshooting

### Problem: "Connection refused"
**Solution:** Server not running. Run `python main.py` in server folder.

### Problem: "MongoDB not connected"
**Solution:** MongoDB not running. Run `mongod --dbpath "C:\data\db"`.

### Problem: "Module not found"
**Solution:** Install dependencies:
```powershell
cd server
pip install -r requirements.txt
```

### Problem: "Port 8000 already in use"
**Solution:** Kill the process:
```powershell
$process = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($process) { Stop-Process -Id $process.OwningProcess -Force }
```

---

## 🎯 What to Test

1. **Authentication Flow**
   - Signup → Login → Access protected pages

2. **Chat System**
   - Create session → Send messages → Verify encryption

3. **Security Features**
   - Send phishing URL → Check detection
   - Send XSS code → Check blocking
   - Send spam → Check filtering

4. **QR Code System**
   - Generate QR → Validate QR → Verify access

---

## 📊 Project Features

### Security Features
- ✅ AES-256-CBC message encryption
- ✅ bcrypt password hashing (12 rounds)
- ✅ JWT authentication (1-hour expiry)
- ✅ ML phishing detection (CatBoost)
- ✅ Rule-based threat detection
- ✅ XSS/injection prevention
- ✅ Spam filtering
- ✅ Rate limiting (30 msg/min)
- ✅ Auto-ban (3 warnings)

### Chat Features
- ✅ Real-time WebSocket chat
- ✅ Multi-user sessions
- ✅ Encrypted messages
- ✅ QR code session sharing
- ✅ Session management

### API Features
- ✅ RESTful API
- ✅ Auto-generated docs (/docs)
- ✅ Content validation endpoint
- ✅ Security reporting
- ✅ User management

---

## 🔗 Important URLs

| URL | Purpose |
|-----|---------|
| http://localhost:8000 | API root |
| http://localhost:8000/docs | API documentation |
| http://localhost:8000/static/signup.html | User signup |
| http://localhost:8000/static/login.html | User login |
| http://localhost:8000/static/index.html | Main app |
| http://localhost:8000/static/chat.html | Chat interface |
| http://localhost:8000/static/validate.html | Validation tool |
| http://localhost:8000/security/status | Security status |

---

## 💡 Pro Tips

1. **Keep terminals open:** One for MongoDB, one for server
2. **Check logs:** Server terminal shows real-time activity
3. **Use DevTools:** Press F12 in browser to see console
4. **Save token:** JWT token needed for authenticated requests
5. **Test in order:** Signup → Login → Create Session → Chat

---

## 🚀 Ready to Start?

```powershell
# Terminal 1: Start MongoDB
mongod --dbpath "C:\data\db"

# Terminal 2: Start Server
cd c:\Users\suman\OneDrive\Documents\cyber\cyberproject\server
python main.py

# Terminal 3: Run Tests
cd c:\Users\suman\OneDrive\Documents\cyber\cyberproject
.\test_api.ps1

# Then open browser
Start-Process "http://localhost:8000/static/signup.html"
```

---

**🎉 You're all set! The project is fully functional and ready to test.**

For detailed testing instructions, see **MANUAL_TESTING_GUIDE.md**
