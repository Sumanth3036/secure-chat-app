#!/usr/bin/env python3
"""
Quick test script to verify email sending functionality
Run this from the server directory: python test_email.py
"""

import asyncio
import sys
import os

# Add parent directory to path to import from main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import send_email_otp, generate_otp, SMTP_USER, SMTP_PASSWORD, SMTP_HOST, SMTP_PORT

async def test_email():
    """Test email sending"""
    print("=" * 60)
    print("📧 Testing OTP Email Functionality")
    print("=" * 60)
    print(f"\nSMTP Configuration:")
    print(f"  Host: {SMTP_HOST}")
    print(f"  Port: {SMTP_PORT}")
    print(f"  User: {SMTP_USER}")
    print(f"  Password: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'Not set'}")
    print()
    
    if not SMTP_USER or not SMTP_PASSWORD:
        print("❌ SMTP credentials not configured!")
        print("   Please add SMTP_USER and SMTP_PASSWORD to your .env file")
        return
    
    # Get email from user
    test_email = input("Enter your email address to test: ").strip()
    if not test_email:
        print("❌ No email provided")
        return
    
    print(f"\n📤 Sending test OTP to {test_email}...")
    
    try:
        otp_code = generate_otp()
        result = await send_email_otp(test_email, otp_code, "signup")
        
        if result:
            print(f"\n✅ Email sent successfully!")
            print(f"   OTP Code: {otp_code}")
            print(f"   Check your inbox at {test_email}")
            print(f"   (Also check spam folder if not in inbox)")
        else:
            print(f"\n❌ Failed to send email")
            print(f"   Check your SMTP configuration and try again")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"   Please check:")
        print(f"   1. SMTP credentials are correct")
        print(f"   2. Google App Password is valid")
        print(f"   3. 2-Step Verification is enabled on your Google account")
        print(f"   4. Internet connection is working")

if __name__ == "__main__":
    asyncio.run(test_email())

