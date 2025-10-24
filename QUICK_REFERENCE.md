# 🛡️ URL Threat Detection - Quick Reference Card

## 🎯 What It Does
Automatically analyzes URLs in chat messages and shows color-coded warnings **before you click**.

---

## 🚦 Threat Levels

| 🟢 **SAFE** | 🟡 **WARNING** | 🔴 **DANGEROUS** |
|-------------|----------------|------------------|
| **< 40%** threat | **40-70%** threat | **> 70%** threat |
| ✅ Click safely | ⚠️ Be careful | 🚫 DO NOT CLICK |
| Legitimate URL | Suspicious patterns | High phishing risk |

---

## 📱 How to Use

### In Chat
1. **Send a message** with a URL
2. **See instant warning** (if threat detected)
3. **Make informed decision** based on color

### Standalone Validation
```
http://localhost:8000/static/validate.html
```

### API Endpoint
```bash
POST /api/validate
{
  "content": "http://example.com",
  "content_type": "url"
}
```

---

## 🎨 Visual Guide

### Safe URL Example
```
┌─────────────────────────────┐
│ 🟢 URL VERIFIED SAFE        │
│ 🤖 ML Score: 12.3%          │
│ ✅ Safe to click            │
└─────────────────────────────┘
```

### Warning Example
```
┌─────────────────────────────┐
│ 🟡 SUSPICIOUS URL           │
│ 🤖 ML Score: 58.7%          │
│ ⚠️ Exercise caution         │
└─────────────────────────────┘
```

### Dangerous Example
```
┌─────────────────────────────┐
│ 🔴 DANGEROUS URL            │
│ 🤖 ML Score: 89.4%          │
│ 🚫 DO NOT CLICK!            │
└─────────────────────────────┘
```

---

## ⚡ Quick Tests

### Test Safe URL
```
https://www.google.com
```
Expected: 🟢 Green

### Test Suspicious URL
```
http://bit.ly/free-offer
```
Expected: 🟡 Yellow

### Test Dangerous URL
```
http://paypal-verify.tk/login
```
Expected: 🔴 Red

---

## 🔍 What Gets Checked

✅ IP addresses in URLs  
✅ URL shorteners (bit.ly, tinyurl)  
✅ Suspicious domains (.tk, .ml, .ga)  
✅ Phishing keywords (login, verify, urgent)  
✅ Brand impersonation (PayPal, Google)  
✅ 25+ more security indicators  

---

## 🚀 Start Testing

```bash
# 1. Start server
cd server
python main.py

# 2. Open chat
http://localhost:8000/static/chat.html?session_id=test

# 3. Send URL
Type: "Check this: http://example.com"

# 4. See warning
Watch for color-coded alert!
```

---

## 📊 Accuracy

- **Model**: CatBoost ML
- **Accuracy**: 96.79%
- **Speed**: < 10ms
- **Features**: 30 indicators

---

## 🆘 Quick Help

**No warning showing?**
- Check if URL is in message
- Verify server is running
- Check browser console

**False positive?**
- Model is 96.79% accurate
- Some legitimate URLs may trigger warnings
- Use your judgment

**Want to test API?**
```bash
python server/test_url_detection.py
```

---

## 📚 Full Documentation

- **Technical**: `URL_THREAT_DETECTION.md`
- **Demo**: `FEATURE_DEMO.md`
- **Summary**: `IMPLEMENTATION_SUMMARY.md`

---

## ✅ Remember

- 🟢 = Safe to click
- 🟡 = Think twice
- 🔴 = Don't click!

**Stay safe! 🛡️**
