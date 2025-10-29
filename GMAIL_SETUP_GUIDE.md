# 📧 Gmail OTP Setup Guide

This guide explains how to configure Gmail for sending OTP emails in the Secure Chat App.

---

## 🔐 Prerequisites

- A Gmail account
- Google Account with 2-Step Verification enabled

---

## 📝 Step-by-Step Setup

### Step 1: Enable 2-Step Verification

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Under "Signing in to Google", click on **2-Step Verification**
4. Follow the prompts to enable 2-Step Verification

### Step 2: Generate App Password

1. After enabling 2-Step Verification, go back to **Security**
2. Under "Signing in to Google", click on **App passwords**
3. You may need to sign in again
4. At the bottom, click on **Select app** and choose **Mail**
5. Click on **Select device** and choose **Other (Custom name)**
6. Enter a name like "Secure Chat App"
7. Click **Generate**
8. Google will display a 16-character app password
9. **Copy this password** - you'll need it for the `.env` file

### Step 3: Configure Environment Variables

1. Open your `.env` file in the project root
2. Add the following lines:

```env
# Gmail SMTP Configuration
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-character-app-password
```

**Example:**
```env
GMAIL_USER=johndoe@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
```

**Note:** The app password will have spaces every 4 characters. You can keep them or remove them - both work.

### Step 4: Test the Configuration

1. Start your server:
```bash
python server/main.py
```

2. Try signing up with a real email address
3. Check if you receive the OTP email

---

## 🧪 Development Mode (Without Gmail)

If you don't configure Gmail credentials, the app will work in **development mode**:

- OTPs will be logged to the console instead of being emailed
- Check the server terminal for OTP codes
- This is useful for testing without email setup

**Console Output Example:**
```
Development OTP for user@example.com: 123456
```

---

## 🔒 Security Best Practices

### ✅ DO:
- Use App Passwords (never your actual Gmail password)
- Keep your `.env` file in `.gitignore`
- Use different app passwords for different applications
- Revoke app passwords when no longer needed

### ❌ DON'T:
- Never commit `.env` file to Git
- Never share your app password
- Don't use your main Gmail password in the app
- Don't hardcode credentials in source code

---

## 🐛 Troubleshooting

### Issue: "Authentication failed"
**Solution:** 
- Verify 2-Step Verification is enabled
- Regenerate the app password
- Check for typos in GMAIL_USER and GMAIL_APP_PASSWORD

### Issue: "SMTP connection timeout"
**Solution:**
- Check your internet connection
- Verify firewall isn't blocking port 587
- Try using a different network

### Issue: "OTP not received"
**Solution:**
- Check spam/junk folder
- Verify the email address is correct
- Check server logs for errors
- Ensure Gmail account is active

### Issue: "App password option not available"
**Solution:**
- Ensure 2-Step Verification is enabled
- Wait a few minutes after enabling 2-Step Verification
- Try accessing from https://myaccount.google.com/apppasswords directly

---

## 📊 Email Features

### OTP Email Includes:
- ✅ Professional HTML template
- ✅ 6-digit OTP code (large and centered)
- ✅ 5-minute expiry notice
- ✅ Security warning
- ✅ Plain text fallback
- ✅ Responsive design

### Email Types:
1. **Email Verification** - During signup
2. **Password Reset** - Forgot password flow

---

## 🔄 Alternative Email Providers

While this guide focuses on Gmail, you can use other SMTP providers:

### Outlook/Hotmail:
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

### Yahoo Mail:
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

### Custom SMTP:
Modify `server/email_service.py` to use your SMTP server settings.

---

## 📞 Support

If you encounter issues:
1. Check server logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test with development mode first (no Gmail config)
4. Ensure Python packages are installed: `pip install -r server/requirements.txt`

---

## ✅ Verification Checklist

- [ ] 2-Step Verification enabled on Gmail
- [ ] App password generated
- [ ] `.env` file created with GMAIL_USER and GMAIL_APP_PASSWORD
- [ ] `.env` file added to `.gitignore`
- [ ] Server restarted after adding credentials
- [ ] Test email sent successfully

---

**Security Note:** App passwords are safer than using your actual password because:
- They can be revoked without changing your main password
- They're app-specific (if compromised, only that app is affected)
- They don't grant access to your full Google Account
- Google monitors their usage for suspicious activity

Happy coding! 🚀
