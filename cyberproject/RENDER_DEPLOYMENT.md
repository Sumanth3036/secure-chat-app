# Render Deployment Guide

## Prerequisites
1. GitHub account with your code pushed
2. Render account (free tier available)
3. MongoDB Atlas account (for database) - optional, can use in-memory storage
4. Gmail App Password (for email sending)

## Step 1: Prepare Your Code

1. Make sure all files are committed to GitHub
2. Update WebSocket URLs in client files (see below)

## Step 2: Deploy Backend to Render

### Option A: Using Render Dashboard

1. Go to https://render.com and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `private-chat-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r server/requirements.txt`
   - **Start Command**: `cd server && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: Leave empty (or set to project root)

5. Add Environment Variables:
   ```
   PORT=8000
   SECRET_KEY=<generate a random 32+ character string>
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_HOURS=1
   AES_SECRET_KEY=<generate a random 32 character string>
   AES_IV=<generate a random 16 character string>
   MONGODB_URL=<your MongoDB Atlas connection string>
   DATABASE_NAME=chat_app
   COLLECTION_NAME=users
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=<your-gmail@gmail.com>
   SMTP_PASSWORD=<your-gmail-app-password>
   SMTP_FROM_NAME=Private Chat
   ```

6. Click "Create Web Service"

### Option B: Using render.yaml

1. Push `render.yaml` to your GitHub repo
2. In Render dashboard, click "New +" → "Blueprint"
3. Connect your repository
4. Render will auto-detect `render.yaml` and create the service
5. Add the environment variables manually in Render dashboard

## Step 3: Update Frontend URLs

After deployment, you'll get a URL like: `https://your-app.onrender.com`

Update these files to use your Render URL:

1. **chat.html** - Line 374: Change WebSocket URL
   ```javascript
   // Change from:
   websocket = new WebSocket(`ws://localhost:8000/ws/${sessionId}?token=${token}`);
   
   // To:
   const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
   const wsHost = window.location.hostname;
   const wsPort = window.location.port ? `:${window.location.port}` : '';
   websocket = new WebSocket(`${wsProtocol}//${wsHost}${wsPort}/ws/${sessionId}?token=${token}`);
   ```

2. **All HTML files** - Update API endpoints from `/send_signup_otp` to use full URL or relative paths

## Step 4: Deploy Frontend (Optional - Static Site)

### Option A: Deploy as Static Site on Render

1. In Render, click "New +" → "Static Site"
2. Connect your GitHub repo
3. Configure:
   - **Name**: `private-chat-frontend`
   - **Root Directory**: `client`
   - **Build Command**: (leave empty)
   - **Publish Directory**: `client`

### Option B: Serve from Backend (Recommended)

The backend already serves static files from `/static` endpoint, so you can access:
- `https://your-app.onrender.com/static/index.html`
- `https://your-app.onrender.com/static/login.html`
- etc.

## Step 5: Generate Environment Variables

### Generate SECRET_KEY (32+ characters):
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Generate AES_SECRET_KEY (exactly 32 characters):
```bash
python -c "import secrets; print(secrets.token_urlsafe(24)[:32])"
```

### Generate AES_IV (exactly 16 characters):
```bash
python -c "import secrets; print(secrets.token_urlsafe(12)[:16])"
```

## Step 6: MongoDB Atlas Setup (Optional)

1. Go to https://www.mongodb.com/cloud/atlas
2. Create free cluster
3. Create database user
4. Whitelist Render IP (or use 0.0.0.0/0 for all)
5. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/`
6. Add to Render environment variables as `MONGODB_URL`

## Step 7: Gmail App Password Setup

1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate app password for "Mail"
5. Use this password (not your regular Gmail password) in `SMTP_PASSWORD`

## Step 8: Test Deployment

1. Visit your Render URL: `https://your-app.onrender.com/static/index.html`
2. Test signup flow
3. Test login
4. Test chat functionality

## Important Notes

- **Free tier limitations**: Render free tier spins down after 15 minutes of inactivity
- **WebSocket support**: Render supports WebSockets, but use `wss://` for HTTPS
- **Environment variables**: Never commit `.env` files to GitHub
- **Static files**: Make sure `client` folder is accessible
- **Port**: Render sets `$PORT` automatically, don't hardcode 8000

## Troubleshooting

1. **Build fails**: Check `requirements.txt` and Python version
2. **WebSocket not working**: Ensure using `wss://` for HTTPS
3. **Static files 404**: Check path in `main.py` (should be `../client`)
4. **Email not sending**: Verify SMTP credentials and app password
5. **Database errors**: Check MongoDB connection string and IP whitelist

## Custom Domain (Optional)

1. In Render dashboard, go to your service
2. Click "Settings" → "Custom Domain"
3. Add your domain
4. Update DNS records as instructed

