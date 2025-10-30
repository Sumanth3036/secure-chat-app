# 🌐 RENDER DEPLOYMENT URLS
## Quick Reference for Faculty Demonstration

---

## 📱 YOUR DEPLOYMENT

**GitHub Repository:**
```
https://github.com/Sumanth3036/secure-chat-app
```

**Render Dashboard:**
```
https://dashboard.render.com
```

---

## 🔗 APPLICATION URLS

> **Note:** Replace `XXXX` with your actual Render deployment ID
> 
> Your URL will look like: `https://secure-chat-app-XXXX.onrender.com`

### **Main Pages:**

| Page | URL | Purpose |
|------|-----|---------|
| **Home** | `/static/index.html` | Landing page |
| **Login** | `/static/login.html` | User login |
| **Signup (OTP)** | `/static/signup_with_otp.html` | New user registration |
| **OTP Verify** | `/static/otp_verify.html` | 6-box OTP interface (NEW) |
| **Forgot Password** | `/static/forgot_password.html` | Password reset with OTP |
| **Chat** | `/static/chat.html` | Encrypted chat interface |
| **QR Generator** | `/static/qr.html` | Generate encrypted QR codes |
| **URL Validator** | `/static/validate.html` | ML phishing detection |
| **API Docs** | `/docs` | Interactive API documentation |

---

## 🔐 ENCRYPTION DEMONSTRATION URLS

### **1. Show Encrypted Chat Messages:**
```
https://secure-chat-app-XXXX.onrender.com/static/chat.html
```
**What to show:** Open DevTools → Network → WebSocket → See encrypted messages

### **2. Show Encrypted QR Tokens:**
```
https://secure-chat-app-XXXX.onrender.com/static/qr.html
```
**What to show:** Generate QR → DevTools → Network → See encrypted token in response

### **3. Show OTP System (NEW 6-box interface):**
```
https://secure-chat-app-XXXX.onrender.com/static/signup_with_otp.html
```
**What to show:** Signup → OTP sent → Check server console → Enter in 6 boxes

### **4. Show JWT Authentication:**
```
https://secure-chat-app-XXXX.onrender.com/static/login.html
```
**What to show:** Login → DevTools → Application → Local Storage → See JWT token

### **5. Show ML Phishing Detection:**
```
https://secure-chat-app-XXXX.onrender.com/static/validate.html
```
**What to show:** Test URLs → See threat scores and ML predictions

---

## 🎯 QUICK DEMO FLOW

### **5-Minute Demo:**

1. **Start:** `https://secure-chat-app-XXXX.onrender.com/static/index.html`
2. **Signup:** Show OTP system with 6-box interface
3. **Login:** Show JWT token in DevTools
4. **Chat:** Show encrypted messages in Network tab
5. **QR Code:** Show encrypted token generation

### **10-Minute Demo:**

1. All of the above, plus:
6. **ML Detection:** Test phishing URLs
7. **Password Reset:** Show OTP system for forgot password
8. **API Docs:** Show `/docs` endpoint

---

## 🔍 HOW TO FIND YOUR RENDER URL

### **Option 1: Render Dashboard**
1. Go to: https://dashboard.render.com
2. Click on your `secure-chat-app` service
3. Look for the URL at the top (e.g., `https://secure-chat-app-abc123.onrender.com`)

### **Option 2: Check Deployment Logs**
1. In Render dashboard
2. Click "Logs" tab
3. Look for: `Uvicorn running on http://0.0.0.0:XXXXX`
4. Your public URL is shown at the top

### **Option 3: Git Remote**
If you've already deployed, check your git config:
```powershell
git config --get remote.render.url
```

---

## 📊 API ENDPOINTS (For Testing)

### **Authentication:**
```
POST /signup          - Create new account
POST /login           - User login
POST /send-otp        - Send OTP for verification
POST /verify-otp      - Verify OTP code
POST /forgot-password - Send password reset OTP
POST /reset-password  - Reset password with OTP
```

### **Chat & Encryption:**
```
POST /chat            - Send encrypted message
GET  /generate_qr     - Generate encrypted QR token
POST /validate_qr     - Validate QR token
```

### **ML Detection:**
```
POST /detect_threat   - Analyze URL for phishing
```

---

## 🧪 TEST COMMANDS

### **Test API Health:**
```powershell
Invoke-RestMethod -Uri "https://secure-chat-app-XXXX.onrender.com/" -Method GET
```

### **Test Encryption Endpoint:**
```powershell
$body = @{
    user_message = "Hello World"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://secure-chat-app-XXXX.onrender.com/chat" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### **Test ML Detection:**
```powershell
$body = @{
    url = "http://paypal-verify.tk/login"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://secure-chat-app-XXXX.onrender.com/detect_threat" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

---

## 🎓 FACULTY PRESENTATION CHECKLIST

### **Before Presentation:**
- [ ] Verify your Render URL is live
- [ ] Test all pages load correctly
- [ ] Check server logs for OTP display
- [ ] Prepare browser with DevTools open
- [ ] Have test URLs ready for ML demo

### **During Presentation:**
- [ ] Show 6-box OTP interface (NEW feature)
- [ ] Demonstrate encrypted chat messages
- [ ] Show encrypted QR tokens
- [ ] Display JWT tokens in DevTools
- [ ] Test ML phishing detection
- [ ] Show password hashing (never plain text)

### **Key Points to Emphasize:**
- [ ] Multiple layers of encryption
- [ ] Industry-standard algorithms (AES-256, bcrypt, JWT)
- [ ] Real-time ML threat detection
- [ ] Modern UX (6-box OTP interface)
- [ ] Security best practices

---

## 🚀 IF YOU NEED TO REDEPLOY

### **Quick Redeploy:**
```powershell
cd c:\Users\suman\OneDrive\Documents\cyber\cyberproject
git add .
git commit -m "Update for faculty demo"
git push origin main
```

Then in Render dashboard:
- Go to your service
- Click "Manual Deploy" → "Deploy latest commit"
- Wait 5-10 minutes for build

---

## 📞 SUPPORT LINKS

**Render Documentation:**
```
https://render.com/docs
```

**FastAPI Documentation:**
```
https://fastapi.tiangolo.com
```

**Your API Docs (Interactive):**
```
https://secure-chat-app-XXXX.onrender.com/docs
```

---

## ✅ VERIFICATION CHECKLIST

After deployment, verify these work:

- [ ] Home page loads
- [ ] Signup with OTP works
- [ ] 6-box OTP interface displays correctly
- [ ] Login works and generates JWT
- [ ] Chat messages are encrypted
- [ ] QR codes generate with encrypted tokens
- [ ] ML detection analyzes URLs
- [ ] Password reset with OTP works
- [ ] API documentation is accessible

---

## 🎉 YOU'RE READY!

**Your application demonstrates:**
1. ✅ AES-256-CBC encryption for messages
2. ✅ Encrypted QR token generation
3. ✅ bcrypt password hashing
4. ✅ JWT authentication
5. ✅ OTP verification system (6-box interface)
6. ✅ ML-based phishing detection (96.79% accuracy)

**Total Security Features:** 6 major encryption/security implementations

---

**Good luck with your faculty presentation! 🎓🔐**
