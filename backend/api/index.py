"""
Vercel Serverless Entry Point for Backend
"""
import sys
import os

# Get paths
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(current_dir)

# Add backend root to sys.path for imports
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# Set environment
os.environ.setdefault('ENVIRONMENT', 'production')

# Create a minimal FastAPI app first for debugging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

debug_app = FastAPI(title="ScamCap API Debug")
debug_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import_errors = []
app_loaded = False

# Try importing the main app
try:
    from app.main import app
    app_loaded = True
except Exception as e:
    import traceback
    import_errors.append({
        "stage": "app.main",
        "error": str(e),
        "traceback": traceback.format_exc()
    })
    app = debug_app

# Add debug endpoints to the app
@app.get("/debug")
def debug_info():
    return {
        "app_loaded": app_loaded,
        "import_errors": import_errors,
        "python_version": sys.version,
        "sys_path": sys.path[:5],
        "backend_root": backend_root,
        "current_dir": current_dir,
        "env_vars": {
            "MONGODB_URL": "SET" if os.getenv("MONGODB_URL") else "NOT SET",
            "JWT_SECRET_KEY": "SET" if os.getenv("JWT_SECRET_KEY") else "NOT SET",
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "NOT SET")
        }
    }

if not app_loaded:
    @app.get("/")
    def root():
        return {
            "status": "error",
            "message": "App failed to load",
            "errors": import_errors
        }
    
    @app.get("/health")
    def health():
        return {
            "status": "error", 
            "message": "App not properly loaded",
            "errors": import_errors
        }

# Handler for Vercel
handler = app
