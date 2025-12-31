"""
Vercel Serverless Entry Point - Production Ready
Supports basic API + optional MFA/Auth features with graceful degradation
Optimized for serverless deployment (no startup/shutdown events)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import re
from typing import Optional, Dict, Any
import os

# Optional imports - graceful degradation if not available
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

try:
    from jose import jwt
    from passlib.context import CryptContext
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title="ScamCap API",
    description="AI-powered phishing and deepfake detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection singleton (lazy initialization)
class DatabaseConnection:
    _instance = None
    _client = None
    _database = None
    _connected = False
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def connect(self):
        """Connect to MongoDB if available and not already connected"""
        if self._connected or not MONGODB_AVAILABLE:
            return self._connected
        
        mongodb_url = os.getenv("MONGODB_URL")
        if not mongodb_url:
            return False
        
        try:
            self._client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=5000)
            self._database = self._client.get_database("scamcap")
            # Test connection
            await self._client.admin.command('ping')
            self._connected = True
            return True
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            self._client = None
            self._database = None
            self._connected = False
            return False
    
    def is_connected(self):
        return self._connected
    
    def get_database(self):
        return self._database if self._connected else None

# Global database instance
db_connection = DatabaseConnection.get_instance()

# Phishing detection logic (inline)
SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.pw', '.cc', '.su', '.buzz', '.work', '.click']
LEGITIMATE_DOMAINS = ['google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'paypal.com', 'microsoft.com', 
                      'apple.com', 'netflix.com', 'instagram.com', 'twitter.com', 'linkedin.com', 'github.com',
                      'whatsapp.com', 'zoom.us', 'dropbox.com', 'spotify.com', 'adobe.com', 'salesforce.com']
BRAND_KEYWORDS = ['paypal', 'amazon', 'google', 'microsoft', 'apple', 'netflix', 'facebook', 'instagram', 
                  'bank', 'secure', 'login', 'verify', 'account', 'update', 'confirm', 'password']

def analyze_url(url: str) -> Dict[str, Any]:
    """Simple phishing analysis"""
    try:
        # Parse URL manually to avoid any dependency issues
        url_lower = url.lower()
        
        # Extract domain
        if '://' in url:
            domain = url.split('://')[1].split('/')[0]
        else:
            domain = url.split('/')[0]
        
        # Remove port if present
        domain = domain.split(':')[0].lower()
        path = url_lower.split(domain)[-1] if domain in url_lower else ""
        
        risk_score = 0.0
        indicators = []
        
        # Check if it's a legitimate domain
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            main_domain = '.'.join(domain_parts[-2:])
            if main_domain in LEGITIMATE_DOMAINS:
                return {"risk_score": 0.0, "indicators": ["✓ Legitimate domain"], "is_safe": True}
        
        # Check suspicious TLDs
        for tld in SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                risk_score += 0.3
                indicators.append(f"⚠️ Suspicious TLD: {tld}")
                break
        
        # Check for brand impersonation
        for brand in BRAND_KEYWORDS[:8]:  # Check main brands
            if brand in domain and not domain.endswith(f'{brand}.com'):
                risk_score += 0.4
                indicators.append(f"🚨 Possible {brand} impersonation")
                break
        
        # Check suspicious keywords in path
        suspicious_path_keywords = ['login', 'verify', 'secure', 'account', 'update', 'confirm', 'suspended']
        for keyword in suspicious_path_keywords:
            if keyword in path:
                risk_score += 0.1
                indicators.append(f"⚠️ Suspicious keyword in URL: {keyword}")
                break
        
        # IP address instead of domain
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
            risk_score += 0.4
            indicators.append("🚨 IP address used instead of domain")
        
        # Cap at 1.0
        risk_score = min(risk_score, 1.0)
        
        return {
            "risk_score": risk_score,
            "indicators": indicators if indicators else ["✓ No obvious threats detected"],
            "is_safe": risk_score < 0.4
        }
    except Exception as e:
        return {"risk_score": 0.5, "indicators": [f"Analysis error: {str(e)}"], "is_safe": False}

@app.get("/")
async def root():
    """Root endpoint with API info"""
    # Lazy connect to database if not already connected
    if MONGODB_AVAILABLE and not db_connection.is_connected():
        await db_connection.connect()
    
    return {
        "message": "ScamCap API is running",
        "version": "1.0.0",
        "status": "healthy",
        "features": {
            "phishing_detection": True,
            "mongodb": MONGODB_AVAILABLE and db_connection.is_connected(),
            "twilio_mfa": TWILIO_AVAILABLE and os.getenv("TWILIO_ACCOUNT_SID") is not None,
            "jwt_auth": AUTH_AVAILABLE and os.getenv("JWT_SECRET_KEY") is not None
        },
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "quick_scan": "/api/v1/test/quick-scan",
            "test_health": "/api/v1/test/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "healthy", "service": "ScamCap API", "timestamp": os.getenv("VERCEL_REGION", "local")}

@app.get("/status")
async def status():
    """Detailed status of all features"""
    # Lazy connect to database if not already connected
    if MONGODB_AVAILABLE and not db_connection.is_connected():
        await db_connection.connect()
    
    db_connected = db_connection.is_connected()
    twilio_configured = os.getenv("TWILIO_ACCOUNT_SID") is not None
    jwt_configured = os.getenv("JWT_SECRET_KEY") is not None
    
    return {
        "api": "operational",
        "deployment": "vercel" if os.getenv("VERCEL") else "local",
        "features": {
            "phishing_detection": {
                "available": True,
                "status": "operational"
            },
            "database": {
                "available": MONGODB_AVAILABLE,
                "connected": db_connected,
                "status": "operational" if db_connected else "unavailable"
            },
            "mfa_sms": {
                "available": TWILIO_AVAILABLE,
                "configured": twilio_configured,
                "status": "operational" if (TWILIO_AVAILABLE and twilio_configured) else "unavailable"
            },
            "authentication": {
                "available": AUTH_AVAILABLE,
                "configured": jwt_configured,
                "status": "operational" if (AUTH_AVAILABLE and jwt_configured) else "unavailable"
            }
        }
    }

@app.post("/api/v1/test/quick-scan")
async def quick_scan(request: dict):
    """
    Quick URL safety check
    
    Accepts: {"url": "https://example.com"}
    Returns: Risk analysis with score, level, and indicators
    """
    try:
        url = request.get("url", "")
        if not url:
            return {"success": False, "error": "URL is required"}
        
        result = analyze_url(url)
        risk_score = result["risk_score"]
        
        # Determine risk level (0-40: SAFE, 40-70: MEDIUM, 70-100: DANGER)
        risk_percent = int(risk_score * 100)
        if risk_percent <= 40:
            risk_level = "SAFE"
            message = "✅ Safe - No threats detected"
        elif risk_percent <= 70:
            risk_level = "MEDIUM"
            message = "⚠️ Medium Risk - Exercise caution"
        else:
            risk_level = "DANGER"
            message = "🚨 High Risk - Potential threat detected"
        
        return {
            "success": True,
            "is_safe": result["is_safe"],
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "message": message,
            "indicators": result["indicators"]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "An error occurred during analysis"
        }

@app.get("/api/v1/test/health")
async def test_health():
    """Test endpoint health check"""
    return {
        "status": "healthy",
        "service": "ScamCap Test API",
        "endpoints": ["quick-scan"]
    }

# Vercel serverless handler
handler = app
