# IPC Debugger - Deployment Guide

This guide will help you deploy your IPC Debugger application so it works on GitHub Pages.

## 📋 Overview

Your project has two parts:
1. **Frontend** (docs/) - Static HTML/CSS/JS → Deployed to GitHub Pages
2. **Backend** (ipc-debugger/) - Python Flask server → Needs to be deployed separately

## 🚀 Step-by-Step Deployment

### Step 1: Deploy Backend to Render.com (Free)

1. **Create a Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure the Service**
   - **Name**: `ipc-debugger-backend` (or any name you prefer)
   - **Root Directory**: `ipc-debugger`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
   - **Instance Type**: `Free`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Copy your deployment URL (e.g., `https://ipc-debugger-backend.onrender.com`)

### Step 2: Update Frontend URLs

Once you have your Render URL, update these files in the `docs/` folder:

1. **docs/js/main.js** (Line 51)
   - Replace `YOUR_RENDER_APP_NAME` with your actual Render app name

2. **docs/js/visualization.js** (Line 106)
   - Replace `YOUR_RENDER_APP_NAME` with your actual Render app name

3. **docs/logs.html** (Lines 199 and 221)
   - Replace `YOUR_RENDER_APP_NAME` with your actual Render app name

**Example**: If your Render URL is `https://ipc-debugger-backend.onrender.com`, replace:
```javascript
'https://YOUR_RENDER_APP_NAME.onrender.com'
```
with:
```javascript
'https://ipc-debugger-backend.onrender.com'
```

### Step 3: Push to GitHub

```bash
cd "c:\Users\aaadi\OneDrive\Desktop\OS - Copy"
git add .
git commit -m "Update frontend URLs for production deployment"
git push origin main
```

### Step 4: Enable GitHub Pages

1. Go to your GitHub repository settings
2. Navigate to "Pages" section
3. Set source to `main` branch and `/docs` folder
4. Save

Your site will be live at: `https://adityaguptaaa.github.io/OS/`

## 🧪 Testing

### Test Locally
```bash
# Terminal 1: Run backend
cd ipc-debugger
python run.py

# Terminal 2: Serve frontend
cd docs
python -m http.server 8000

# Open: http://localhost:8000
```

### Test Production
1. Open: `https://adityaguptaaa.github.io/OS/`
2. Create a simulation
3. Check browser console for any errors

## ⚠️ Important Notes

1. **Free Tier Limitations**:
   - Render free tier spins down after 15 minutes of inactivity
   - First request after spin-down takes 30-60 seconds to wake up

2. **CORS**: Your backend already has CORS enabled (`CORS(app)` in app.py)

3. **WebSocket**: Make sure your Render deployment supports WebSocket connections

## 🐛 Troubleshooting

**Issue**: "Failed to connect to backend"
- Solution: Check if Render service is running (it may be spinning up)
- Wait 60 seconds and try again

**Issue**: "CORS error"
- Solution: Verify CORS is enabled in backend/app.py

**Issue**: "WebSocket connection failed"
- Solution: Ensure you're using `https://` (not `http://`) for production URLs

## 📝 Files Modified

- ✅ `ipc-debugger/render.yaml` - Render deployment config
- ✅ `ipc-debugger/Procfile` - Process file for deployment
- ✅ `docs/js/main.js` - Auto-detect environment for API calls
- ✅ `docs/js/visualization.js` - Auto-detect environment for WebSocket
- ✅ `docs/logs.html` - Auto-detect environment for exports

## 🎉 Next Steps

After deployment:
1. Test all features on the live site
2. Share your live URL: `https://adityaguptaaa.github.io/OS/`
3. Monitor backend logs on Render dashboard
