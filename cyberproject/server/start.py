#!/usr/bin/env python3
"""
Startup wrapper script with error handling
"""
import sys
import os
import traceback

print("=" * 60, flush=True)
print("Starting Secure Chat Application", flush=True)
print("=" * 60, flush=True)

try:
    # Try to import the app
    print("\n1. Importing main module...", flush=True)
    from main import app
    print("   ✅ Main module imported successfully", flush=True)
    
    # Get port from environment
    port = int(os.getenv("PORT", 8000))
    print(f"\n2. Starting server on port {port}...", flush=True)
    
    # Import uvicorn
    import uvicorn
    print("   ✅ Uvicorn imported", flush=True)
    
    # Start the server
    print(f"\n3. Launching application...", flush=True)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Startup Error: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

