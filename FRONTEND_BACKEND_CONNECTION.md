# Frontend-Backend Connection Guide

##  Setup Complete!

### Files Created:

1. **frontend/src/lib/api.ts** - API client and configuration
2. **frontend/.env.local** - Environment variables for API URL
3. **frontend/src/components/QuickScanForm.tsx** - Example component

---

##  Configuration Steps

### 1. Update Environment Variables

**For Local Development:**
\\\ash
# frontend/.env.local (already created)
NEXT_PUBLIC_API_URL=http://localhost:8000
\\\

**For Production:**
After deploying backend to Vercel, update:
\\\ash
NEXT_PUBLIC_API_URL=https://your-backend-domain.vercel.app
\\\

### 2. Backend CORS (Already Configured)
 Backend already allows all origins
 No changes needed

---

##  How to Use

### Option 1: Use the API Client

\\\	ypescript
import { apiClient } from '@/lib/api';

// Quick scan (no auth)
const result = await apiClient.quickScan('https://example.com');

// Login
await apiClient.login('user@example.com', 'password');

// Phishing analysis (requires auth)
const analysis = await apiClient.analyzePhishing('https://suspicious.com');
\\\

### Option 2: Use API Endpoints Directly

\\\	ypescript
import { API_ENDPOINTS } from '@/lib/api';

const response = await fetch(API_ENDPOINTS.quickScan, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://example.com' })
});
\\\

### Option 3: Use the Example Component

Add to any page:
\\\	ypescript
import QuickScanForm from '@/components/QuickScanForm';

export default function Page() {
  return <QuickScanForm />;
}
\\\

---

##  Available API Endpoints

### Public (No Auth Required)
- \POST /api/v1/test/quick-scan\ - Quick URL safety check
- \GET /api/v1/test/health\ - Health check
- \GET /health\ - Basic health check

### Auth
- \POST /api/v1/auth/register\ - Register new user
- \POST /api/v1/auth/login\ - Login and get token

### Protected (Requires Auth Token)
- \POST /api/v1/phishing/analyze\ - Phishing analysis
- \POST /api/v1/deepfake/analyze-image\ - Image deepfake detection
- \POST /api/v1/deepfake/analyze-video\ - Video deepfake detection

---

##  Testing

### 1. Start Backend (Local)
\\\ash
cd backend
python -m uvicorn app.main:app --reload
\\\

### 2. Start Frontend
\\\ash
cd frontend
npm run dev
\\\

### 3. Test Connection
Visit http://localhost:3000 and use the QuickScanForm component

---

##  Production Deployment

### 1. Deploy Backend to Vercel
\\\ash
cd backend
vercel --prod
\\\
Note your backend URL (e.g., https://backend-xxx.vercel.app)

### 2. Update Frontend Environment
\\\ash
# frontend/.env.local
NEXT_PUBLIC_API_URL=https://your-backend-xxx.vercel.app
\\\

### 3. Deploy Frontend to Vercel
\\\ash
cd frontend
vercel --prod
\\\

### 4. Set Environment Variables in Vercel Dashboard
For frontend project:
- \NEXT_PUBLIC_API_URL\ = your backend URL

---

##  Authentication Flow

\\\	ypescript
import { apiClient } from '@/lib/api';

// 1. Login
const response = await apiClient.login('user@example.com', 'password');
// Token is automatically saved

// 2. Make authenticated requests
const result = await apiClient.analyzePhishing('https://site.com');

// 3. Logout
apiClient.clearToken();
\\\

---

##  Troubleshooting

### CORS Error
-  Already fixed - backend allows all origins
- If issues persist, check browser console

### Connection Refused
- Ensure backend is running on port 8000
- Check NEXT_PUBLIC_API_URL is correct

### 401 Unauthorized
- Login first to get auth token
- Token expires after 30 minutes

---

##  Example: Full Integration

\\\	ypescript
'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

export default function Dashboard() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = async () => {
    try {
      await apiClient.login('user@example.com', 'password');
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleScan = async () => {
    try {
      const result = await apiClient.quickScan('https://example.com');
      console.log(result);
    } catch (error) {
      console.error('Scan failed:', error);
    }
  };

  return (
    <div>
      {!isLoggedIn ? (
        <button onClick={handleLogin}>Login</button>
      ) : (
        <button onClick={handleScan}>Scan URL</button>
      )}
    </div>
  );
}
\\\

---

**All set! Your frontend is ready to connect to your backend.** 
