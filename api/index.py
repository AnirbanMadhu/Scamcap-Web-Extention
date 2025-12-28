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
    from backend.app.main import app

# Vercel handler
handler = app
