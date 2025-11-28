#!/usr/bin/env python3
"""
Simple backend test without running server
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

def test_imports():
    """Test if all backend imports work"""
    try:
        print("Testing backend imports...")
        
        # Test settings
        from backend.app.config.settings import get_settings
        settings = get_settings()
        print(f"✅ Settings loaded: {settings.api_host}:{settings.api_port}")
        
        # Test database
        from backend.app.config.database import Database
        print("✅ Database module imported")
        
        # Test models
        from backend.app.models.schemas import ThreatType
        print("✅ Schemas imported")
        
        print("\n🎉 All backend imports working!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
