#!/usr/bin/env python3
"""
Check if all required modules are installed
"""

import sys

required_modules = {
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'passlib': 'passlib',
    'pydantic': 'pydantic',
    'pymongo': 'pymongo',
    'motor': 'motor',
    'qrcode': 'qrcode',
    'jwt': 'PyJWT',
    'cryptography': 'cryptography',
    'dotenv': 'python-dotenv',
    'catboost': 'catboost',
    'sklearn': 'scikit-learn',
    'joblib': 'joblib'
}

missing_modules = []
installed_modules = []

print("=" * 60)
print("Checking Required Modules")
print("=" * 60)
print()

for module_name, package_name in required_modules.items():
    try:
        __import__(module_name)
        installed_modules.append(package_name)
        print(f"✅ {package_name:20s} - Installed")
    except ImportError:
        missing_modules.append(package_name)
        print(f"❌ {package_name:20s} - MISSING")

print()
print("=" * 60)
if missing_modules:
    print(f"❌ {len(missing_modules)} module(s) missing:")
    for mod in missing_modules:
        print(f"   - {mod}")
    print()
    print("To install missing modules, run:")
    print("   pip install " + " ".join(missing_modules))
else:
    print("✅ All required modules are installed!")
print("=" * 60)

sys.exit(0 if not missing_modules else 1)

