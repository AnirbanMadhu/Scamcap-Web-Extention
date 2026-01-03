from http.server import BaseHTTPRequestHandler
import json
import re
from urllib.parse import parse_qs, urlparse

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

class handler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
        
        path = self.path
        
        if path == '/' or path == '':
            response = {
                "message": "ScamCap API is running",
                "version": "1.0.0",
                "status": "healthy",
                "endpoints": {
                    "health": "/health",
                    "quick_scan": "/api/v1/test/quick-scan (POST)",
                    "docs": "/docs"
                }
            }
        elif path == '/health' or path == '/status':
            response = {"status": "healthy", "service": "ScamCap API"}
        elif path == '/api/v1/test/health':
            response = {"status": "healthy", "service": "ScamCap Test API"}
        else:
            response = {"error": "Not found", "path": path}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/api/v1/test/quick-scan':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                url = data.get('url', '')
                if not url:
                    self.send_response(400)
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "URL required"}).encode())
                    return
                
                result = analyze_url(url)
                risk_score = result["risk_score"]
                risk_percent = int(risk_score * 100)
                
                if risk_percent <= 40:
                    risk_level, message = "SAFE", "✅ Safe - No threats detected"
                elif risk_percent <= 70:
                    risk_level, message = "MEDIUM", "⚠️ Medium Risk - Exercise caution"
                else:
                    risk_level, message = "DANGER", "🚨 High Risk - Potential threat"
                
                response = {
                    "success": True,
                    "is_safe": result["is_safe"],
                    "risk_score": round(risk_score, 2),
                    "risk_level": risk_level,
                    "message": message,
                    "indicators": result["indicators"]
                }
                
                self.send_response(200)
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                self.send_response(500)
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
        else:
            self.send_response(404)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
