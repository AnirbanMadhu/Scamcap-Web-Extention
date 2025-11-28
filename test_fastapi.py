#!/usr/bin/env python3
"""
Simple FastAPI test
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

def test_fastapi_creation():
    """Test if FastAPI app can be created"""
    try:
        print("Testing FastAPI app creation...")
        
        from backend.app.main import app
        print("✅ FastAPI app created successfully")
        
        # Test if app has routes
        routes = [route.path for route in app.routes]
        print(f"✅ App has {len(routes)} routes: {routes}")
        
        return True
        
    except Exception as e:
        print(f"❌ FastAPI creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fastapi_creation()
