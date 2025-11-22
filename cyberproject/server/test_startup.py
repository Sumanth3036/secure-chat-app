#!/usr/bin/env python3
"""
Test script to diagnose startup issues
"""
import sys
import traceback

print("=" * 60)
print("Testing Application Startup")
print("=" * 60)

# Test 1: Basic imports
print("\n1. Testing basic imports...")
try:
    import fastapi
    print("   ✅ fastapi")
except Exception as e:
    print(f"   ❌ fastapi: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    import uvicorn
    print("   ✅ uvicorn")
except Exception as e:
    print(f"   ❌ uvicorn: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Import main module
print("\n2. Testing main.py import...")
try:
    from main import app
    print("   ✅ main.py imported successfully")
    print(f"   ✅ FastAPI app created: {app.title}")
except Exception as e:
    print(f"   ❌ Failed to import main.py: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check if app can be accessed
print("\n3. Testing app object...")
try:
    print(f"   ✅ App title: {app.title}")
    print(f"   ✅ App version: {app.version}")
    print(f"   ✅ Routes count: {len(app.routes)}")
except Exception as e:
    print(f"   ❌ App access failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All startup tests passed!")
print("=" * 60)
sys.exit(0)




