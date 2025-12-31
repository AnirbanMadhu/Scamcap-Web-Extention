#!/usr/bin/env python3
"""
Test script to verify the Vercel deployment works correctly
Run this after deploying to test all endpoints
"""
import json
import sys

# Test data
TEST_URL_SAFE = "https://google.com"
TEST_URL_SUSPICIOUS = "https://paypa1-secure.tk/login"

print("=" * 60)
print("ScamCap API Deployment Verification")
print("=" * 60)

# Get deployment URL from user
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1].rstrip('/')
else:
    BASE_URL = input("Enter your Vercel deployment URL (e.g., https://your-app.vercel.app): ").rstrip('/')

print(f"\nTesting API at: {BASE_URL}")
print("-" * 60)

try:
    import requests
except ImportError:
    print("❌ ERROR: 'requests' library not found.")
    print("Install it with: pip install requests")
    sys.exit(1)

def test_endpoint(name, method, url, data=None):
    """Test an API endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=10)
        
        print(f"\n✅ {name}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2)[:200]}...")
            return True
        else:
            print(f"   ❌ FAILED: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"\n❌ {name}")
        print(f"   ERROR: {str(e)}")
        return False

# Run tests
results = []

print("\n1. Testing Root Endpoint")
results.append(test_endpoint("Root /", "GET", f"{BASE_URL}/"))

print("\n2. Testing Health Check")
results.append(test_endpoint("Health Check", "GET", f"{BASE_URL}/health"))

print("\n3. Testing Quick Scan (Safe URL)")
results.append(test_endpoint(
    "Quick Scan - Safe",
    "POST",
    f"{BASE_URL}/api/v1/test/quick-scan",
    {"url": TEST_URL_SAFE}
))

print("\n4. Testing Quick Scan (Suspicious URL)")
results.append(test_endpoint(
    "Quick Scan - Suspicious",
    "POST",
    f"{BASE_URL}/api/v1/test/quick-scan",
    {"url": TEST_URL_SUSPICIOUS}
))

print("\n5. Testing Test Health Endpoint")
results.append(test_endpoint("Test Health", "GET", f"{BASE_URL}/api/v1/test/health"))

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
passed = sum(results)
total = len(results)
print(f"Tests Passed: {passed}/{total}")

if passed == total:
    print("\n🎉 ALL TESTS PASSED! Your deployment is working perfectly!")
    sys.exit(0)
else:
    print(f"\n⚠️ {total - passed} test(s) failed. Check the errors above.")
    sys.exit(1)
