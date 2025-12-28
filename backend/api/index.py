import sys
import os

# Ensure app directory is in path for Vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from app.main import app
except Exception as e:
    # If import fails, create a minimal error reporting app
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    def error():
        return {
            "error": "Import failed",
            "message": str(e),
            "path": sys.path,
            "cwd": os.getcwd()
        }
