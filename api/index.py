from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import re
from typing import Dict, Any
import os

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

# Phishing detection constants
SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.pw', '.cc', '.su', '.buzz', '.work', '.click']
LEGITIMATE_DOMAINS = ['google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'paypal.com', 'microsoft.com', 
                      'apple.com', 'netflix.com', 'instagram.com', 'twitter.com', 'linkedin.com', 'github.com',
                      'whatsapp.com', 'zoom.us', 'dropbox.com', 'spotify.com', 'adobe.com', 'salesforce.com']
BRAND_KEYWORDS = ['paypal', 'amazon', 'google', 'microsoft', 'apple', 'netflix', 'facebook', 'instagram', 
                  'bank', 'secure', 'login', 'verify', 'account', 'update', 'confirm', 'password']

def analyze_url(url: str) -> Dict[str, Any]:
    """Simple phishing analysis"""
    try:
        url_lower = url.lower()
        
        # Extract domain
        if '://' in url:
            domain = url.split('://')[1].split('/')[0]
        else:
            domain = url.split('/')[0]
        
        domain = domain.split(':')[0].lower()
        path = url_lower.split(domain)[-1] if domain in url_lower else ""
        
        risk_score = 0.0
        indicators = []
        
        # Check legitimate domains
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
        
        # Check brand impersonation
        for brand in BRAND_KEYWORDS[:8]:
            if brand in domain and not domain.endswith(f'{brand}.com'):
                risk_score += 0.4
                indicators.append(f"🚨 Possible {brand} impersonation")
                break
        
        # Check suspicious keywords
        suspicious_path_keywords = ['login', 'verify', 'secure', 'account', 'update', 'confirm', 'suspended']
        for keyword in suspicious_path_keywords:
            if keyword in path:
                risk_score += 0.1
                indicators.append(f"⚠️ Suspicious keyword in URL: {keyword}")
                break
        
        # IP address check
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
            risk_score += 0.4
            indicators.append("🚨 IP address used instead of domain")
        
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
    """Root endpoint"""
    return {
        "message": "ScamCap API is running",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "quick_scan": "/api/v1/test/quick-scan",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "service": "ScamCap API"}

@app.get("/status")
async def status():
    """Status check"""
    return {
        "api": "operational",
        "deployment": "vercel" if os.getenv("VERCEL") else "local",
        "features": {
            "phishing_detection": {"available": True, "status": "operational"}
        }
    }

@app.post("/api/v1/test/quick-scan")
async def quick_scan(request: dict):
    """Quick URL safety check"""
    try:
        url = request.get("url", "")
        if not url:
            return {"success": False, "error": "URL is required"}
        
        result = analyze_url(url)
        risk_score = result["risk_score"]
        
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
        return {"success": False, "error": str(e)}

@app.get("/api/v1/test/health")
async def test_health():
    """Test endpoint health"""
    return {"status": "healthy", "service": "ScamCap Test API"}

# Vercel handler - FastAPI app instance
handler = app
