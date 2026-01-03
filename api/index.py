from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
import re

# Create FastAPI app
app = FastAPI(
    title="ScamCap API",
    description="AI-powered phishing and deepfake detection",
    version="1.0.0"
)

# Request models
class QuickScanRequest(BaseModel):
    url: str

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.pw', '.cc', '.su', '.buzz', '.work', '.click']
LEGITIMATE_DOMAINS = ['google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'paypal.com', 'microsoft.com', 
                      'apple.com', 'netflix.com', 'instagram.com', 'twitter.com', 'linkedin.com', 'github.com']
BRAND_KEYWORDS = ['paypal', 'amazon', 'google', 'microsoft', 'apple', 'netflix', 'facebook', 'instagram', 
                  'bank', 'secure', 'login', 'verify', 'account', 'update', 'confirm', 'password']

def analyze_url(url: str):
    """Analyze URL for phishing indicators"""
    try:
        url_lower = url.lower()
        domain = url.split('://')[1].split('/')[0] if '://' in url else url.split('/')[0]
        domain = domain.split(':')[0].lower()
        path = url_lower.split(domain)[-1] if domain in url_lower else ""
        
        risk_score = 0.0
        indicators = []
        
        # Check legitimate
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            main_domain = '.'.join(domain_parts[-2:])
            if main_domain in LEGITIMATE_DOMAINS:
                return {"risk_score": 0.0, "indicators": ["✓ Legitimate domain"], "is_safe": True}
        
        # Suspicious TLD
        for tld in SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                risk_score += 0.3
                indicators.append(f"⚠️ Suspicious TLD: {tld}")
                break
        
        # Brand impersonation
        for brand in BRAND_KEYWORDS[:8]:
            if brand in domain and not domain.endswith(f'{brand}.com'):
                risk_score += 0.4
                indicators.append(f"🚨 Possible {brand} impersonation")
                break
        
        # Suspicious keywords
        for keyword in ['login', 'verify', 'secure', 'account', 'update', 'confirm', 'suspended']:
            if keyword in path:
                risk_score += 0.1
                indicators.append(f"⚠️ Suspicious keyword: {keyword}")
                break
        
        # IP address
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
            risk_score += 0.4
            indicators.append("🚨 IP address used")
        
        risk_score = min(risk_score, 1.0)
        return {
            "risk_score": risk_score,
            "indicators": indicators if indicators else ["✓ No threats detected"],
            "is_safe": risk_score < 0.4
        }
    except Exception as e:
        return {"risk_score": 0.5, "indicators": [f"Error: {str(e)}"], "is_safe": False}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ScamCap API is running",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "quick_scan": "/api/v1/test/quick-scan",
            "docs": "/docs"
        }
    }

# Health check endpoints
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ScamCap API"}

@app.get("/status")
async def status():
    return {"api": "operational", "features": {"phishing_detection": True}}

@app.get("/api/v1/test/health")
async def test_health():
    return {"status": "healthy", "service": "ScamCap Test API"}

# Quick scan endpoint
@app.post("/api/v1/test/quick-scan")
async def quick_scan(request: QuickScanRequest):
    try:
        url = request.url
        if not url:
            return JSONResponse({"success": False, "error": "URL required"}, status_code=400)
        
        result = analyze_url(url)
        risk_score = result["risk_score"]
        risk_percent = int(risk_score * 100)
        
        if risk_percent <= 40:
            risk_level, message = "SAFE", "✅ Safe - No threats detected"
        elif risk_percent <= 70:
            risk_level, message = "MEDIUM", "⚠️ Medium Risk - Exercise caution"
        else:
            risk_level, message = "DANGER", "🚨 High Risk - Potential threat"
        
        return {
            "success": True,
            "is_safe": result["is_safe"],
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "message": message,
            "indicators": result["indicators"]
        }
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

# OPTIONS for CORS preflight
@app.options("/api/v1/test/quick-scan")
async def quick_scan_options():
    return {}

# Vercel serverless function handler
from mangum import Mangum
handler = Mangum(app, lifespan="off", api_gateway_base_path="/")

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
