#!/usr/bin/env python3
"""
Startup check script - tests if the application can start without errors
"""
import sys
import os

print("=" * 60)
print("Startup Check - Testing Imports")
print("=" * 60)

errors = []

# Test critical imports
try:
    import fastapi
    print("✅ fastapi")
except Exception as e:
    errors.append(f"fastapi: {e}")
    print(f"❌ fastapi: {e}")

try:
    import uvicorn
    print("✅ uvicorn")
except Exception as e:
    errors.append(f"uvicorn: {e}")
    print(f"❌ uvicorn: {e}")

try:
    from cryptography.hazmat.primitives.ciphers import Cipher
    print("✅ cryptography")
except Exception as e:
    errors.append(f"cryptography: {e}")
    print(f"❌ cryptography: {e}")

try:
    from passlib.hash import bcrypt
    print("✅ passlib")
except Exception as e:
    errors.append(f"passlib: {e}")
    print(f"❌ passlib: {e}")

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    print("✅ motor")
except Exception as e:
    errors.append(f"motor: {e}")
    print(f"❌ motor: {e}")

try:
    from security_monitor import security_monitor
    print("✅ security_monitor")
except Exception as e:
    errors.append(f"security_monitor: {e}")
    print(f"❌ security_monitor: {e}")

try:
    from ml_detector import get_detector
    print("✅ ml_detector")
except Exception as e:
    errors.append(f"ml_detector: {e}")
    print(f"❌ ml_detector: {e}")

print("=" * 60)
if errors:
    print(f"❌ {len(errors)} import error(s) found")
    sys.exit(1)
else:
    print("✅ All critical imports successful")
    sys.exit(0)




