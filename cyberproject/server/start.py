#!/usr/bin/env python3
"""
Startup wrapper script with error handling
"""
import sys
import os
import traceback

# Set unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

print("=" * 60)
print("Starting Secure Chat Application")
print("=" * 60)

try:
    # Try to import the app
    print("\n1. Importing main module...")
    from main import app
    print("   ✅ Main module imported successfully")
    
    # Get port from environment
    port = int(os.getenv("PORT", 8000))
    print(f"\n2. Starting server on port {port}...")
    
    # Import uvicorn
    import uvicorn
    print("   ✅ Uvicorn imported")
    
    # Start the server
    print(f"\n3. Launching application...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    traceback.print_exc()
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Startup Error: {e}")
    traceback.print_exc()
    sys.exit(1)

