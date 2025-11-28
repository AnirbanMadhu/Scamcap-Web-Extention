#!/usr/bin/env python3
"""
Comprehensive test suite for ScamCap Extension
"""
import sys
import os
import requests
import time
import json

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

def test_backend_comprehensive():
    """Comprehensive backend test"""
    print("🔍 COMPREHENSIVE BACKEND TEST")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    tests = [
        {
            "name": "Root Endpoint",
            "method": "GET",
            "url": f"{base_url}/",
            "expected_status": 200
        },
        {
            "name": "Health Check",
            "method": "GET", 
            "url": f"{base_url}/health",
            "expected_status": 200
        },
        {
            "name": "API Documentation",
            "method": "GET",
            "url": f"{base_url}/docs",
            "expected_status": 200
        },
        {
            "name": "OpenAPI Schema",
            "method": "GET",
            "url": f"{base_url}/openapi.json",
            "expected_status": 200
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test["method"] == "GET":
                response = requests.get(test["url"], timeout=5)
            elif test["method"] == "POST":
                response = requests.post(test["url"], json=test.get("data", {}), timeout=5)
            
            if response.status_code == test["expected_status"]:
                print(f"✅ {test['name']}: PASSED ({response.status_code})")
                passed += 1
            else:
                print(f"❌ {test['name']}: FAILED (Expected {test['expected_status']}, got {response.status_code})")
                failed += 1
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {test['name']}: FAILED (Connection refused - is server running?)")
            failed += 1
        except Exception as e:
            print(f"❌ {test['name']}: FAILED ({str(e)})")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0

def test_backend_imports():
    """Test backend imports"""
    print("\n🔍 BACKEND IMPORTS TEST")
    print("=" * 30)
    
    imports = [
        ("Settings", "from backend.app.config.settings import get_settings"),
        ("Database", "from backend.app.config.database import Database"),
        ("Schemas", "from backend.app.models.schemas import ThreatType"),
        ("FastAPI App", "from backend.app.main import app"),
        ("Auth Service", "from backend.app.services.auth_service import AuthService"),
        ("Phishing Detector", "from backend.app.services.phishing_detector import PhishingDetector")
    ]
    
    passed = 0
    failed = 0
    
    for name, import_statement in imports:
        try:
            exec(import_statement)
            print(f"✅ {name}: IMPORTED")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: FAILED ({str(e)})")
            failed += 1
    
    print(f"\n📊 Import Results: {passed} passed, {failed} failed")
    return failed == 0

def test_extension_files():
    """Test extension files exist and are valid"""
    print("\n🔍 EXTENSION FILES TEST")
    print("=" * 30)
    
    required_files = [
        "extension/manifest.json",
        "extension/popup/popup.html",
        "extension/popup/popup.js",
        "extension/popup/styles.css",
        "extension/background/service-worker.js",
        "extension/content/content-script.js",
        "extension/content/content-styles.css"
    ]
    
    passed = 0
    failed = 0
    
    for file_path in required_files:
        if os.path.exists(file_path):
            # Check if file is not empty
            if os.path.getsize(file_path) > 0:
                print(f"✅ {file_path}: EXISTS")
                passed += 1
            else:
                print(f"❌ {file_path}: EMPTY")
                failed += 1
        else:
            print(f"❌ {file_path}: MISSING")
            failed += 1
    
    # Validate manifest.json
    try:
        with open("extension/manifest.json", 'r') as f:
            manifest = json.load(f)
        
        required_manifest_fields = ["manifest_version", "name", "version", "permissions"]
        for field in required_manifest_fields:
            if field in manifest:
                print(f"✅ Manifest {field}: PRESENT")
                passed += 1
            else:
                print(f"❌ Manifest {field}: MISSING")
                failed += 1
                
    except Exception as e:
        print(f"❌ Manifest validation: FAILED ({str(e)})")
        failed += 1
    
    print(f"\n📊 Extension Results: {passed} passed, {failed} failed")
    return failed == 0

def test_environment():
    """Test environment setup"""
    print("\n🔍 ENVIRONMENT TEST")
    print("=" * 25)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check virtual environment
    venv_path = "d:\\Coding Junction\\Projects\\ScamCap Extention\\venvs\\scamcap"
    if os.path.exists(venv_path):
        print(f"✅ Virtual Environment: EXISTS at {venv_path}")
    else:
        print(f"❌ Virtual Environment: MISSING")
    
    # Check key packages
    packages = ["fastapi", "uvicorn", "pydantic", "motor", "transformers", "torch"]
    for package in packages:
        try:
            __import__(package)
            print(f"✅ Package {package}: INSTALLED")
        except ImportError:
            print(f"❌ Package {package}: MISSING")
    
    return True

def main():
    """Run all tests"""
    print("🚀 SCAMCAP EXTENSION - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    # Test environment
    env_success = test_environment()
    
    # Test backend imports
    import_success = test_backend_imports()
    
    # Test extension files
    extension_success = test_extension_files()
    
    # Test backend API (if server is running)
    print("\n⏳ Waiting for server to be ready...")
    time.sleep(2)
    api_success = test_backend_comprehensive()
    
    # Overall results
    print("\n" + "=" * 60)
    print("🏆 OVERALL TEST RESULTS")
    print("=" * 60)
    
    results = [
        ("Environment Setup", env_success),
        ("Backend Imports", import_success),
        ("Extension Files", extension_success),
        ("API Endpoints", api_success)
    ]
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:20}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! ScamCap Extension is ready to use!")
        print("\n📋 Next Steps:")
        print("1. Keep the API server running")
        print("2. Load the extension in Chrome (chrome://extensions/)")
        print("3. Test the extension functionality")
        print("4. Visit http://localhost:8000/docs for API documentation")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    main()
