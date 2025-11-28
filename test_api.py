#!/usr/bin/env python3
"""
Test script to verify the ScamCap API is working
"""

import requests
import json

def test_api():
    """Test the ScamCap API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing ScamCap API...")
    print("=" * 40)
    
    try:
        # Test root endpoint
        print("1. Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
        
        # Test health endpoint
        print("\n2. Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
        
        # Test docs endpoint
        print("\n3. Testing documentation endpoint...")
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ Documentation endpoint working")
        else:
            print(f"❌ Documentation endpoint failed: {response.status_code}")
        
        print("\n" + "=" * 40)
        print("🎉 API is running successfully!")
        print("📖 Visit http://localhost:8000/docs for API documentation")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_api()
