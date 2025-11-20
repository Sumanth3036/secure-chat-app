# Email Setup Guide for OTP Functionality

## ✅ Your Current Configuration

Based on your `.docker.env` file, you have:
- **SMTP_HOST**: smtp.gmail.com
- **SMTP_PORT**: 587
- **SMTP_USER**: sumanthponugupati@gmail.com
- **SMTP_PASSWORD**: cpbe lqhl bxui mvaz (Google App Password)
- **SMTP_FROM_NAME**: secure

## 📧 How OTP Emails Work

1. **When you sign up or request password reset**, the server will:
   - Generate a 6-digit OTP code
   - Send it via email using your Gmail SMTP settings
   - Store the OTP in the database with a 5-minute expiry

2. **Email sending process**:
   - Server checks if `SMTP_USER` and `SMTP_PASSWORD` are configured
   - If configured: Sends email via Gmail SMTP
   - If not configured: Prints OTP to console (development mode)

## ✅ Will It Work?

**YES!** Your configuration looks correct. The OTP emails should work because:

1. ✅ Gmail SMTP settings are correct (`smtp.gmail.com:587`)
2. ✅ You're using a Google App Password (required for Gmail SMTP)
3. ✅ The code handles spaces in App Passwords automatically
4. ✅ Error handling is in place

## 🚀 Testing

To test if emails are working:

1. **Start the server**:
   ```bash
   cd cyberproject/server
   python main.py
   ```

2. **Check the startup logs** - You should see:
   ```
   - OTP System: ✅ Enabled (SMTP configured)
   - SMTP Server: smtp.gmail.com:587
   - SMTP User: sumanthponugupati@gmail.com
   ```

3. **Try signing up** - Go to `/static/signup.html` and:
   - Enter an email address
   - Enter a password
   - Click "Send Verification OTP"
   - Check your email inbox (and spam folder)

4. **Check server logs** - You should see:
   ```
   ✅ OTP email sent successfully to [email]
   ```

## ⚠️ Common Issues & Solutions

### Issue 1: "SMTP Authentication failed"
**Solution**: 
- Make sure you're using a **Google App Password**, not your regular Gmail password
- To create an App Password:
  1. Go to Google Account → Security
  2. Enable 2-Step Verification (if not already enabled)
  3. Go to App Passwords
  4. Generate a new app password for "Mail"
  5. Use that 16-character password (spaces are OK, they're auto-removed)

### Issue 2: "Connection timeout"
**Solution**:
- Check your internet connection
- Make sure port 587 is not blocked by firewall
- Try using port 465 with SSL instead (requires code change)

### Issue 3: Emails going to spam
**Solution**:
- This is normal for automated emails
- Check spam/junk folder
- Mark as "Not Spam" to improve deliverability

### Issue 4: "Less secure app access" error
**Solution**:
- Google no longer supports "less secure apps"
- You **MUST** use App Passwords (which you're already doing ✅)

## 🌐 Deployment on Render

When deploying to Render:

1. **Set Environment Variables** in Render dashboard:
   - `SMTP_HOST` = `smtp.gmail.com`
   - `SMTP_PORT` = `587`
   - `SMTP_USER` = `sumanthponugupati@gmail.com`
   - `SMTP_PASSWORD` = `cpbe lqhl bxui mvaz` (your App Password)
   - `SMTP_FROM_NAME` = `secure`
   - Plus all other variables from `.docker.env`

2. **The code automatically loads** environment variables, so emails will work the same way

3. **Security Note**: Never commit `.docker.env` to Git! Use Render's environment variable settings instead.

## 📝 Email Template

The OTP email includes:
- Professional HTML design
- Large, easy-to-read OTP code
- Expiry time (5 minutes)
- Security warning
- Both HTML and plain text versions

## 🔍 Debugging

If emails aren't working:

1. **Check server logs** for error messages
2. **Verify SMTP credentials** are correct
3. **Test with a simple email** first
4. **Check Gmail account** for security alerts
5. **Verify App Password** is still valid (they can be revoked)

## ✅ Verification Checklist

- [x] SMTP_HOST is set to `smtp.gmail.com`
- [x] SMTP_PORT is set to `587`
- [x] SMTP_USER is your Gmail address
- [x] SMTP_PASSWORD is a Google App Password (16 characters)
- [x] Code handles spaces in App Password
- [x] Error handling is in place
- [x] Email template is ready

**Your setup should work!** 🎉




