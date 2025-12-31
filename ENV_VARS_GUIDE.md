# Environment Variables Configuration

## Required for Vercel Deployment

### Basic API (Already Working)
No environment variables needed! The API works out of the box with phishing detection.

### Full Features (MFA + Authentication + Database)

Add these environment variables in your Vercel Dashboard:
**Project → Settings → Environment Variables**

#### 1. MongoDB (Required for user accounts and data persistence)
```
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/scamcap?retryWrites=true&w=majority
```

#### 2. JWT Authentication (Required for secure login)
```
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRES_HOURS=24
```

#### 3. Twilio SMS/MFA (Required for multi-factor authentication)
```
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

#### 4. Optional Configuration
```
ENVIRONMENT=production
PHISHING_RISK_THRESHOLD=0.7
DEEPFAKE_RISK_THRESHOLD=0.8
MFA_TRIGGER_THRESHOLD=0.9
```

## Feature Status Endpoint

Check which features are available:
```bash
curl https://your-app.vercel.app/status
```

Response shows:
- `phishing_detection` - Always available ✅
- `database` - Available if MongoDB configured
- `mfa_sms` - Available if Twilio configured
- `authentication` - Available if JWT configured

## How It Works

The API uses **graceful degradation**:
- ✅ Basic phishing detection works without any env vars
- ✅ Each feature checks if its dependencies are available
- ✅ Missing features don't crash the API
- ✅ Status endpoint shows what's enabled

## Local Development

Copy your `.env` file values to Vercel:

```bash
# From your local .env file
MONGODB_URL=...
JWT_SECRET_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...
```

## Testing

After setting environment variables:

1. **Check status:**
   ```bash
   curl https://your-app.vercel.app/status
   ```

2. **Test phishing detection (always works):**
   ```bash
   curl -X POST https://your-app.vercel.app/api/v1/test/quick-scan \
     -H "Content-Type: application/json" \
     -d '{"url": "https://suspicious-site.tk"}'
   ```

3. **Test with full features (when configured):**
   - User registration (needs MongoDB + JWT)
   - MFA verification (needs Twilio)
   - Threat logging (needs MongoDB)

## Security Notes

⚠️ **Never commit these values to Git!**
- Keep `.env` in `.gitignore`
- Use Vercel's environment variables for production
- Rotate secrets regularly
- Use strong JWT secret (min 32 characters)

## Quick Setup Guide

1. **Deploy without env vars** - Basic API works immediately
2. **Add MongoDB** - Enables user accounts and data storage
3. **Add JWT** - Enables secure authentication
4. **Add Twilio** - Enables SMS-based MFA

Each feature activates automatically when its env vars are present! 🚀
