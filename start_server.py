#!/usr/bin/env python3
"""
ScamCap API Server - Main Entry Point
Runs all backend services: Phishing Detection, Deepfake Detection, MFA, Authentication
"""
import sys
import os
import uvicorn
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

# Load environment variables
load_dotenv()

def print_banner():
    """Print startup banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                    ScamCap API Server                     ║
    ║        AI-Powered Phishing & Deepfake Detection           ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Services:                                                ║
    ║    ✓ Phishing Detection API                               ║
    ║    ✓ Deepfake Detection API                               ║
    ║    ✓ Multi-Factor Authentication (SMS)                    ║
    ║    ✓ User Authentication & Authorization                  ║
    ║    ✓ Threat Logging & Analytics                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_environment():
    """Check required environment variables and configurations"""
    print("\n[*] Checking environment configuration...")
    
    # Check MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/scamcap")
    print(f"    MongoDB: {mongodb_url}")
    
    # Check JWT
    jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    if jwt_secret and jwt_secret != "your-super-secret-jwt-key-here-change-this-in-production":
        print("    JWT Secret: Configured ✓")
    else:
        print("    JWT Secret: Using default (change in production) ⚠")
    
    # Check Twilio (SMS MFA)
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    if twilio_sid:
        print("    Twilio SMS: Configured ✓")
    else:
        print("    Twilio SMS: Not configured (SMS MFA disabled)")
    
    # Check ML Models
    phishing_model = os.getenv("PHISHING_MODEL_PATH", "backend/ml-models/phishing/bert_phishing_model.pth")
    deepfake_model = os.getenv("DEEPFAKE_MODEL_PATH", "backend/ml-models/deepfake/efficientnet_deepfake_model.pth")
    print(f"    Phishing Model: {phishing_model}")
    print(f"    Deepfake Model: {deepfake_model}")
    
    print("\n[*] Environment check complete.\n")

def run_server():
    """Start the uvicorn server with all services"""
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    workers = int(os.getenv("API_WORKERS", 1))
    environment = os.getenv("ENVIRONMENT", "development")
    
    print(f"[*] Starting server on http://{host}:{port}")
    print(f"[*] Environment: {environment}")
    print(f"[*] API Documentation: http://localhost:{port}/docs")
    print(f"[*] Health Check: http://localhost:{port}/health")
    print("\n" + "="*60 + "\n")
    
    # Run with reload in development, without in production
    reload_enabled = environment == "development"
    
    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        reload=reload_enabled,
        workers=workers if not reload_enabled else 1,
        log_level="info"
    )

if __name__ == "__main__":
    print_banner()
    check_environment()
    
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n[*] Server shutdown requested.")
    except Exception as e:
        print(f"\n[!] Server startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
