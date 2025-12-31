"""
Vercel Serverless Entry Point
This file serves as the main entry point for Vercel serverless functions.
"""
import sys
import os

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, 'backend')

# Add paths to sys.path for imports
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up environment
os.environ.setdefault('ENVIRONMENT', 'production')

# Import the FastAPI app
try:
    from backend.app.main import app
except ImportError:
    try:
        from app.main import app
    except ImportError as e:
        import traceback
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(title="ScamCap API - Error Mode")
        
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
                "traceback": traceback.format_exc(),
                "sys_path": sys.path[:5],
                "project_root": project_root,
                "backend_path": backend_path,
                "cwd": os.getcwd()
            }
        
        @app.get("/health")
        def health():
            return {"status": "error", "message": "App not properly loaded"}

# Handler for Vercel
handler = app
