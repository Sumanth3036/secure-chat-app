# Quick Render Deployment Checklist

## Before Deploying

- [ ] Push all code to GitHub
- [ ] Test locally to ensure everything works
- [ ] Have Gmail App Password ready
- [ ] Have MongoDB Atlas connection string (optional)

## Deployment Steps

### 1. Create Render Account
- Go to https://render.com
- Sign up with GitHub

### 2. Create Web Service
- Click "New +" → "Web Service"
- Connect GitHub repository
- Select your repository

### 3. Configure Service
- **Name**: `private-chat-backend`
- **Environment**: `Python 3`
- **Region**: Choose closest to you
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty
- **Build Command**: `pip install -r server/requirements.txt`
- **Start Command**: `cd server && uvicorn main:app --host 0.0.0.0 --port $PORT`

### 4. Add Environment Variables

Click "Advanced" → "Add Environment Variable" for each:

```
SECRET_KEY = <generate 32+ char random string>
AES_SECRET_KEY = <generate exactly 32 char string>
AES_IV = <generate exactly 16 char string>
SMTP_USER = your-email@gmail.com
SMTP_PASSWORD = your-gmail-app-password
MONGODB_URL = mongodb+srv://user:pass@cluster.mongodb.net/ (optional)
```

**Generate secrets:**
```bash
# SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# AES_SECRET_KEY (32 chars)
python -c "import secrets; print(secrets.token_urlsafe(24)[:32])"

# AES_IV (16 chars)
python -c "import secrets; print(secrets.token_urlsafe(12)[:16])"
```

### 5. Deploy
- Click "Create Web Service"
- Wait for build to complete (5-10 minutes first time)
- Copy your URL: `https://your-app.onrender.com`

### 6. Test
- Visit: `https://your-app.onrender.com/static/index.html`
- Test signup, login, chat

## Important Notes

1. **Free tier**: Service sleeps after 15 min inactivity (takes ~30 sec to wake)
2. **WebSocket**: Already configured to use `wss://` automatically
3. **Static files**: Served from `/static/` endpoint
4. **Email**: Must use Gmail App Password, not regular password

## Troubleshooting

- **Build fails**: Check Python version (should be 3.10+)
- **404 on static files**: Check that `client` folder is in repo
- **WebSocket errors**: Ensure using HTTPS (wss://)
- **Email not sending**: Verify App Password is correct

## Your App URL Structure

After deployment:
- Home: `https://your-app.onrender.com/static/index.html`
- Login: `https://your-app.onrender.com/static/login.html`
- Signup: `https://your-app.onrender.com/static/signup.html`
- Chat: `https://your-app.onrender.com/static/chat.html?session_id=...`

