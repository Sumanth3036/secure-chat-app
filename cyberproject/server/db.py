import os
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

# Read MongoDB URI from environment, fallback to local default for dev
MONGODB_URI = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

# Create Motor client and database handle
client: AsyncIOMotorClient = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
# Use the database name from environment variable or default to cyberproject
DB_NAME = os.getenv("DATABASE_NAME", "cyberproject")
DB = client[DB_NAME]

# Expose collections
users = DB["users"]
messages = DB["messages"]
qrcodes = DB["qrcodes"]

# Ensure indexes on startup
async def ensure_indexes() -> None:
    await users.create_index("email", unique=True)
    await messages.create_index([("room", 1), ("timestamp", 1)])
    await qrcodes.create_index("token", unique=True)

# Try to schedule index creation if an event loop is running
try:
    # Test connection to MongoDB Atlas
    try:
        client.admin.command('ping')
        logging.info("Successfully connected to MongoDB Atlas")
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        logging.error(f"Failed to connect to MongoDB Atlas: {e}")
        
    loop = asyncio.get_running_loop()
    loop.create_task(ensure_indexes())
except RuntimeError:
    # No running loop at import time; main app should call ensure_indexes() on startup
    pass
