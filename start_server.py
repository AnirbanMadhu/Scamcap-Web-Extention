#!/usr/bin/env python3
"""
Manual server startup to test the application
"""
import sys
import os
import uvicorn

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

if __name__ == "__main__":
    print("Starting ScamCap API server...")
    
    try:
        uvicorn.run(
            "backend.app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"Server startup error: {e}")
        import traceback
        traceback.print_exc()
