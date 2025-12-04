#!/usr/bin/env python3
"""
Docker Integration Test

Validates Meridian 3.0 Docker deployment.

Run: python tests/integration/docker_integration_test.py

Author: Meridian Team
Date: December 4, 2025
"""

import requests
import time
import subprocess

print("\n" + "="*70)
print("🐳 MERIDIAN 3.0 DOCKER INTEGRATION TEST")
print("="*70)
print()

def check_docker():
    """Check if Docker is running"""
    try:
        subprocess.run(['docker', 'ps'], capture_output=True, check=True)
        return True
    except:
        print("❌ Docker is not running or not installed")
        return False

def test_api_container():
    """Test API container"""
    print("Testing API container...")
    
    # Wait for container to be ready
    max_retries = 10
    for i in range(max_retries):
        try:
            res = requests.get("http://localhost:8000/health", timeout=2)
            if res.status_code == 200:
                print("   ✅ API container is healthy")
                return True
        except:
            if i < max_retries - 1:
                print(f"   ⏳ Waiting for API container ({i+1}/{max_retries})...")
                time.sleep(3)
    
    print("   ❌ API container failed to respond")
    return False

def test_dashboard_container():
    """Test dashboard container"""
    print("Testing Dashboard container...")
    
    try:
        res = requests.get("http://localhost:8501", timeout=5)
        if res.status_code == 200:
            print("   ✅ Dashboard container is accessible")
            return True
    except:
        print("   ⚠️  Dashboard container not accessible")
        print("      (This is normal if not running)")
        return False

def test_api_endpoints():
    """Test critical API endpoints"""
    print("Testing API endpoints...")
    
    endpoints = [
        "/",
        "/health",
        "/docs"
    ]
    
    all_passed = True
    for endpoint in endpoints:
        try:
            res = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if res.status_code == 200:
                print(f"   ✅ {endpoint}")
            else:
                print(f"   ❌ {endpoint} - Status {res.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ {endpoint} - {str(e)[:50]}")
            all_passed = False
    
    return all_passed

# Run tests
print("Checking Docker...")
if not check_docker():
    print("\n⚠️  Docker not available. Install Docker to run container tests.")
    print("   Local tests can still run without Docker.\n")
    exit(0)

print("\nℹ️  Make sure containers are running:")
print("   cd deploy && docker-compose up -d")
print()

input("Press Enter when containers are ready (or Ctrl+C to skip)...")

print()
api_ok = test_api_container()
dashboard_ok = test_dashboard_container()
endpoints_ok = test_api_endpoints() if api_ok else False

print()
print("=" * 70)
print("📊 DOCKER TEST RESULTS")
print("=" * 70)
print()

if api_ok and endpoints_ok:
    print("╔════════════════════════════════════════════════════════╗")
    print("║                                                        ║")
    print("║    🎊 DOCKER DEPLOYMENT VALIDATED! 🎊                  ║")
    print("║                                                        ║")
    print("║    Meridian 3.0 is ready for production deployment    ║")
    print("║                                                        ║")
    print("╚════════════════════════════════════════════════════════╝")
else:
    print("⚠️  Some Docker tests failed - review containers")

print()

