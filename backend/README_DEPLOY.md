# ScamCap Backend - Vercel Deployment

##  This Backend Folder is Ready for Vercel Deployment!

###  Backend Structure (Deploy This Folder Only)
```
backend/
 api/
    index.py              # Vercel entry point
 app/
    main.py              # FastAPI application
    api/routes/          # API routes
    config/              # Configuration
    models/              # Data models
    services/            # Business logic
 requirements.txt          # Python dependencies
 vercel.json              # Vercel configuration
 .vercelignore            # Files to exclude
```

###  Deployment Steps

#### 1. Deploy to Vercel
1. Go to https://vercel.com/new
2. Click "Import Project"
3. **IMPORTANT**: Select the **backend** folder only (not the root)
4. Vercel will auto-detect the configuration
5. Click "Deploy"

#### 2. Set Environment Variables in Vercel Dashboard
Go to Project Settings  Environment Variables and add:

**Required:**
- `MONGODB_URL` = your-mongodb-atlas-connection-string
- `JWT_SECRET_KEY` = your-secure-random-secret-key

**Optional (for MFA features):**
- `TWILIO_ACCOUNT_SID` = your-twilio-account-sid
- `TWILIO_AUTH_TOKEN` = your-twilio-auth-token
- `TWILIO_PHONE_NUMBER` = your-twilio-phone-number

#### 3. MongoDB Atlas Setup
1. Create free cluster at https://cloud.mongodb.com
2. Create database user
3. **Important**: Whitelist IP  Add `0.0.0.0/0` (allow all)
4. Get connection string and replace `<db_password>` with your password
5. Add to Vercel environment variables

###  Test Your Deployment
After deployment, visit:
- `https://your-domain.vercel.app/`  Welcome message
- `https://your-domain.vercel.app/health`  Health check
- `https://your-domain.vercel.app/docs`  API Documentation (Swagger)
- `https://your-domain.vercel.app/api/v1/test/health`  API health endpoint

###  Available Endpoints
- `/` - Root endpoint
- `/health` - Health check
- `/docs` - Interactive API documentation
- `/redoc` - Alternative API documentation
- `/api/v1/test/*` - Test endpoints (no auth required)
- `/api/v1/phishing/*` - Phishing detection (requires auth)
- `/api/v1/deepfake/*` - Deepfake detection (requires auth)
- `/api/v1/auth/*` - Authentication (register/login)
- `/api/v1/mfa/*` - Multi-factor authentication

###  What's Optimized
-  Lightweight dependencies (no heavy ML libraries)
-  Serverless-compatible file operations
-  Environment variables read from Vercel
-  Async MongoDB with Motor
-  JWT authentication with bcrypt
-  CORS configured
-  Auto-generated API docs

###  Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python -m uvicorn app.main:app --reload

# Or use the provided start script
python ../start_server.py
```

###  Troubleshooting
- **404 Error**: Make sure you selected the `backend` folder, not root
- **Import Errors**: Check Vercel build logs for missing dependencies
- **Database Connection**: Verify MongoDB Atlas IP whitelist includes 0.0.0.0/0
- **Environment Variables**: Ensure all required vars are set in Vercel dashboard

###  Notes
- Extension and ML models are excluded from deployment (.vercelignore)
- Database connections are handled async for serverless
- All routes are serverless-compatible
- Maximum file upload size: 100MB (configurable)

---
**Ready to Deploy!** Just select the backend folder in Vercel. 
