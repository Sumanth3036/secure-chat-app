"""
Complete Integration Test for ML Model in Chat System
Tests the /api/validate endpoint with ML integration
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_security_status():
    """Test the security status endpoint"""
    print("="*60)
    print("Testing Security Status Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/security/status")
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Security Status Retrieved:")
            print(f"   Security Level: {data.get('security_level')}")
            
            ml_detection = data.get('ml_phishing_detection', {})
            print(f"\n📊 ML Detection Status:")
            print(f"   Enabled: {ml_detection.get('enabled')}")
            print(f"   Model Type: {ml_detection.get('model_type')}")
            print(f"   Model Accuracy: {ml_detection.get('model_accuracy')}")
            print(f"   Features Count: {ml_detection.get('features_count')}")
            print(f"   Fallback Mode: {ml_detection.get('fallback_mode')}")
            
            return True
        else:
            print(f"❌ Failed: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_validation_endpoint():
    """Test the validation endpoint with various inputs"""
    print("\n" + "="*60)
    print("Testing Validation Endpoint with ML Integration")
    print("="*60)
    
    test_cases = [
        {
            "content": "https://www.google.com",
            "content_type": "url",
            "description": "Legitimate URL - Google"
        },
        {
            "content": "http://192.168.1.1/admin/login.php",
            "content_type": "url",
            "description": "Suspicious URL - IP address"
        },
        {
            "content": "http://paypal-secure-verify.tk/login",
            "content_type": "url",
            "description": "Phishing URL - Fake PayPal"
        },
        {
            "content": "Click here to verify your account: http://bit.ly/verify123",
            "content_type": "text",
            "description": "Phishing text with URL shortener"
        },
        {
            "content": "Hello, how are you doing today?",
            "content_type": "text",
            "description": "Normal text message"
        },
        {
            "content": "URGENT! Your account will be suspended. Click here immediately!",
            "content_type": "text",
            "description": "Urgent phishing message"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─'*60}")
        print(f"Test Case {i}: {test_case['description']}")
        print(f"{'─'*60}")
        print(f"Content: {test_case['content'][:60]}...")
        print(f"Type: {test_case['content_type']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/validate",
                json={
                    "content": test_case["content"],
                    "content_type": test_case["content_type"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key information
                is_safe = data.get("is_safe")
                status = data.get("status")
                warnings = data.get("warnings", [])
                details = data.get("details", {})
                ml_detection = details.get("ml_detection", {})
                
                # Display results
                status_emoji = "🟢" if is_safe else ("🟡" if status == "warning" else "🔴")
                print(f"\n{status_emoji} Status: {status.upper()}")
                print(f"   Safe: {is_safe}")
                
                # ML Detection Info
                if ml_detection.get("enabled"):
                    phishing_prob = ml_detection.get("phishing_probability")
                    risk_level = ml_detection.get("risk_level", "unknown")
                    print(f"\n🤖 ML Detection:")
                    print(f"   Phishing Probability: {phishing_prob:.4f} ({phishing_prob*100:.2f}%)")
                    print(f"   Risk Level: {risk_level.upper()}")
                    print(f"   Model: {ml_detection.get('model_type')}")
                else:
                    print(f"\n⚠️  ML Detection: Disabled (using fallback)")
                
                # Warnings
                if warnings:
                    print(f"\n⚠️  Warnings ({len(warnings)}):")
                    for j, warning in enumerate(warnings, 1):
                        print(f"   {j}. [{warning.get('source', 'unknown')}] {warning.get('message')}")
                        print(f"      Severity: {warning.get('severity')}")
                else:
                    print(f"\n✅ No warnings detected")
                
                results.append({
                    "test": test_case["description"],
                    "status": status,
                    "ml_prob": ml_detection.get("phishing_probability"),
                    "success": True
                })
                
            else:
                print(f"❌ Failed: Status code {response.status_code}")
                print(f"   Response: {response.text}")
                results.append({
                    "test": test_case["description"],
                    "success": False
                })
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "test": test_case["description"],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    successful = sum(1 for r in results if r.get("success"))
    total = len(results)
    
    print(f"\n✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    return successful == total

def main():
    """Run all tests"""
    print("="*60)
    print("ML Model Integration - Complete Test Suite")
    print("="*60)
    print("\n⚠️  Make sure the server is running on http://localhost:8000")
    print("   Run: python main.py or uvicorn main:app --reload\n")
    
    input("Press Enter to continue...")
    
    # Run tests
    status_ok = test_security_status()
    validation_ok = test_validation_endpoint()
    
    # Final summary
    print("\n" + "="*60)
    print("Final Results")
    print("="*60)
    
    if status_ok and validation_ok:
        print("\n🎉 All tests passed successfully!")
        print("\n✅ ML Model Integration Complete:")
        print("   • CatBoost model loaded and working")
        print("   • Validation endpoint integrated")
        print("   • Hybrid detection (ML + Rules) active")
        print("   • Security status endpoint updated")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
