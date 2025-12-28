"""
Vercel Serverless Entry Point
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

# Import after path setup
try:
    from app.main import app
except ImportError:
    try:
        from backend.app.main import app
    except ImportError as e:
        # Fallback: create minimal app if imports fail
        from fastapi import FastAPI
        app = FastAPI()
        
        @app.get("/")
        def root():
            return {"error": f"Import failed: {str(e)}", "message": "Check deployment logs"}

# Export for Vercel
app = app
