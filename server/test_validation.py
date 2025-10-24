#!/usr/bin/env python3
"""
Test script for the validation endpoint
"""

import requests
import json

def test_validation_endpoint():
    """Test the validation endpoint with various content types"""
    
    base_url = "http://localhost:8000"
    
    # Test cases
    test_cases = [
        {
            "name": "Safe Text",
            "content": "Hello! This is a normal message with no security threats.",
            "content_type": "text"
        },
        {
            "name": "Phishing URL",
            "content": "Click here to verify your account: https://paypal-secure-verify.tk/login",
            "content_type": "url"
        },
        {
            "name": "XSS Attack",
            "content": "<script>alert('XSS')</script>",
            "content_type": "text"
        },
        {
            "name": "Spam Content",
            "content": "Make money fast! Click here for free  casino bonuses!",
            "content_type": "text"
        },
        {
            "name": "Safe URL",
            "content": "https://www.google.com",
            "content_type": "url"
        }
    ]
    
    print("🧪 Testing Security Validation Endpoint")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"Content: {test_case['content'][:50]}...")
        
        try:
            response = requests.post(
                f"{base_url}/api/validate",
                headers={"Content-Type": "application/json"},
                json={
                    "content": test_case["content"],
                    "content_type": test_case["content_type"]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                status_icon = "✅" if result["is_safe"] else "❌"
                print(f"{status_icon} Status: {result['status'].upper()}")
                print(f"   Warnings: {len(result['warnings'])}")
                
                for warning in result['warnings']:
                    print(f"   ⚠️  {warning['type']}: {warning['message']}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Server not running")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Validation endpoint test completed!")

if __name__ == "__main__":
    test_validation_endpoint()

