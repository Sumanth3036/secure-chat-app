#!/usr/bin/env python3
"""
Server startup script with graceful MongoDB handling
"""

import asyncio
import uvicorn
from main import app
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def startup_with_mongo_retry():
    """Startup function with MongoDB connection retry"""
    try:
        # Try to connect to MongoDB
        from main import connect_to_mongo
        await connect_to_mongo()
        logger.info("✅ MongoDB connected successfully")
    except Exception as e:
        logger.warning(f"⚠️  MongoDB connection failed: {e}")
        logger.info("🔄 Starting server without MongoDB (some features may be limited)")
    
    logger.info("🚀 Server starting...")

async def shutdown_graceful():
    """Graceful shutdown function"""
    try:
        from main import close_mongo_connection
        await close_mongo_connection()
        logger.info("✅ MongoDB connection closed")
    except Exception as e:
        logger.warning(f"⚠️  Error closing MongoDB connection: {e}")
    
    logger.info("🛑 Server shutdown complete")

if __name__ == "__main__":
    # Override the startup and shutdown events
    app.router.startup = startup_with_mongo_retry
    app.router.shutdown = shutdown_graceful
    
    print("🔐 Secure Chat Server with Hybrid Security Validation")
    print("=" * 60)
    print("Features:")
    print("  ✅ JWT Authentication")
    print("  ✅ AES-256-CBC Encryption")
    print("  ✅ bcrypt Password Hashing")
    print("  ✅ Security Monitoring (Phishing/XSS/Spam)")
    print("  ✅ Hybrid Security Validation System")
    print("  ✅ QR Code Security")
    print("=" * 60)
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )

