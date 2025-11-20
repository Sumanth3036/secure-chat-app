#!/bin/bash
# Start script for Render deployment
# This script ensures the server starts correctly on Render

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start uvicorn server
# Render sets PORT environment variable automatically
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

