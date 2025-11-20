@echo off
echo Installing Python dependencies for CYBERPROJECT...
echo.

echo Installing FastAPI and dependencies...
pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo To run the server, use: python main.py
echo Or: uvicorn main:app --reload
pause






