"""
Vercel Serverless Entry Point for Backend
This serves the FastAPI application when the backend folder is deployed separately.
"""
import sys
import os
import traceback

# Get paths
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(current_dir)

# Add backend root to sys.path for imports
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# Set environment
os.environ.setdefault('ENVIRONMENT', 'production')

# Import the FastAPI app
try:
    from app.main import app
    print("Successfully imported app from app.main")
except ImportError as e:
    error_tb = traceback.format_exc()
    print(f"Import error: {e}")
    print(f"Traceback: {error_tb}")
    
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(title="ScamCap API - Import Error")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    def root():
        return {
            "error": "Import failed",
            "message": str(e),
            "traceback": error_tb,
            "backend_root": backend_root,
            "current_dir": current_dir,
            "sys_path": sys.path[:5],
            "env_vars": {
                "MONGODB_URL": "set" if os.getenv("MONGODB_URL") else "NOT SET",
                "JWT_SECRET_KEY": "set" if os.getenv("JWT_SECRET_KEY") else "NOT SET",
                "ENVIRONMENT": os.getenv("ENVIRONMENT", "NOT SET")
            }
        }
    
    @app.get("/health")
    def health():
        return {"status": "error", "message": "App not properly loaded", "error": str(e)}

# Handler for Vercel
handler = app
