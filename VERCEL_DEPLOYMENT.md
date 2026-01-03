# ScamCap Vercel Deployment Guide

## Overview

This project consists of three parts:
1. **Backend (API)** - FastAPI Python server for phishing/deepfake detection
2. **Frontend** - Next.js website for downloading the extension
3. **Extension** - Chrome/Edge browser extension

## Deployment Steps

### Step 1: Deploy Backend API to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. **Important Settings:**
   - **Root Directory:** `backend`
   - **Framework Preset:** Other
   - **Build Command:** (leave empty)
   - **Output Directory:** (leave empty)

5. Add Environment Variables:
   ```
   MONGODB_URL=your_mongodb_connection_string
   JWT_SECRET_KEY=your-super-secret-key-for-production
   ENVIRONMENT=production
   ```

6. Click "Deploy"

7. After deployment, copy your backend URL (e.g., `https://scamcap-backend.vercel.app`)

### Step 2: Update Extension API URL

Before deploying frontend, update the extension with your backend URL:

1. Open `backend/extension/background/service-worker.js`
2. Find this line:
   ```javascript
   const API_BASE_URL = 'https://scamcap-api.vercel.app/api/v1';
   ```
3. Replace with your backend URL:
   ```javascript
   const API_BASE_URL = 'https://your-backend-url.vercel.app/api/v1';
   ```

### Step 3: Deploy Frontend to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import the same repository (or a separate one if you split them)
4. **Important Settings:**
   - **Root Directory:** `frontend`
   - **Framework Preset:** Next.js
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

5. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.vercel.app
   ```

6. Click "Deploy"

### Step 4: Install Extension in Browser

#### For Chrome:
1. Visit your frontend website
2. Download the extension zip file
3. Extract the zip file to a folder
4. Open Chrome and go to `chrome://extensions/`
5. Enable "Developer mode" (top right toggle)
6. Click "Load unpacked"
7. Select the extracted `scamcap-extension` folder

#### For Edge:
1. Visit your frontend website
2. Download the extension zip file
3. Extract the zip file to a folder
4. Open Edge and go to `edge://extensions/`
5. Enable "Developer mode" (left sidebar)
6. Click "Load unpacked"
7. Select the extracted `scamcap-extension` folder

## Environment Variables Reference

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/scamcap` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | `your-secure-random-string` |
| `ENVIRONMENT` | Environment name | `production` |
| `TWILIO_ACCOUNT_SID` | (Optional) Twilio SID for MFA | `AC...` |
| `TWILIO_AUTH_TOKEN` | (Optional) Twilio token | `...` |
| `TWILIO_PHONE_NUMBER` | (Optional) Twilio phone | `+1...` |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://scamcap-backend.vercel.app` |

## Troubleshooting

### API Returns Import Error
- Check that all Python dependencies are in `requirements.txt`
- Verify the `backend/api/index.py` file exists
- Check Vercel deployment logs for specific import errors

### Extension Can't Connect to API
- Verify the API URL in `service-worker.js` is correct
- Check browser console for CORS errors
- Ensure backend is deployed and accessible

### Download Button Doesn't Work
- Check frontend deployment logs
- Verify the extension folder path is correct
- Ensure `archiver` package is installed

### CORS Errors
- The backend is configured to allow all origins
- If still having issues, check Vercel's `vercel.json` headers configuration

## API Endpoints

### Public Endpoints (No Auth Required)
- `GET /` - API info
- `GET /health` - Health check
- `POST /api/v1/test/quick-scan` - Quick URL scan
- `GET /api/v1/test/health` - Test endpoint

### Protected Endpoints (Require Auth)
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/phishing/analyze` - Full phishing analysis
- `POST /api/v1/deepfake/analyze-image` - Image analysis
- `POST /api/v1/deepfake/analyze-video` - Video analysis

## MongoDB Setup (Free Option)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create a database user
4. Whitelist all IPs (0.0.0.0/0) for Vercel
5. Get your connection string
6. Add it to Vercel environment variables

## Testing Your Deployment

### Test Backend:
```bash
curl https://your-backend-url.vercel.app/health
```

Expected response:
```json
{"status": "healthy", "service": "ScamCap API"}
```

### Test Quick Scan:
```bash
curl -X POST https://your-backend-url.vercel.app/api/v1/test/quick-scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'
```

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check browser developer console
3. Verify all environment variables are set
4. Ensure MongoDB connection is working
