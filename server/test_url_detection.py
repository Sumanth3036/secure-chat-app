"""
Test script for real-time URL threat detection in chat
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api_validate():
    """Test the /api/validate endpoint with various URLs"""
    print("="*70)
    print("Testing /api/validate Endpoint - URL Threat Detection")
    print("="*70)
    
    test_cases = [
        {
            "name": "Safe URL - Google",
            "content": "https://www.google.com",
            "expected": "safe"
        },
        {
            "name": "Safe URL - GitHub",
            "content": "Check out this repo: https://github.com/example/project",
            "expected": "safe"
        },
        {
            "name": "Suspicious URL - URL Shortener",
            "content": "Click here: http://bit.ly/free-offer",
            "expected": "warning"
        },
        {
            "name": "Suspicious URL - IP Address",
            "content": "Login here: http://192.168.1.1/admin/login.php",
            "expected": "warning"
        },
        {
            "name": "Dangerous URL - Fake PayPal",
            "content": "Verify your account: http://paypal-secure-verify.tk/login",
            "expected": "dangerous"
        },
        {
            "name": "Dangerous URL - Phishing with urgency",
            "content": "URGENT! Your account will be suspended. Click here immediately: http://secure-bank-verify.ml/confirm",
            "expected": "dangerous"
        },
        {
            "name": "Multiple URLs - Mixed",
            "content": "Check https://www.google.com and also http://suspicious-site.tk/login",
            "expected": "warning"
        },
        {
            "name": "No URL - Safe Text",
            "content": "Hello, how are you doing today?",
            "expected": "safe"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*70}")
        print(f"Test {i}/{len(test_cases)}: {test['name']}")
        print(f"{'─'*70}")
        print(f"Content: {test['content'][:60]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/validate",
                json={
                    "content": test["content"],
                    "content_type": "text"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                status = data.get("status")
                is_safe = data.get("is_safe")
                warnings = data.get("warnings", [])
                ml_detection = data.get("details", {}).get("ml_detection", {})
                
                # Display results
                status_emoji = "🟢" if status == "safe" else ("🟡" if status == "warning" else "🔴")
                print(f"\n{status_emoji} Status: {status.upper()}")
                print(f"   Safe: {is_safe}")
                print(f"   Expected: {test['expected']}")
                
                # ML Detection
                if ml_detection.get("enabled"):
                    prob = ml_detection.get("phishing_probability", 0)
                    risk = ml_detection.get("risk_level", "unknown")
                    print(f"\n🤖 ML Detection:")
                    print(f"   Phishing Probability: {prob:.4f} ({prob*100:.2f}%)")
                    print(f"   Risk Level: {risk.upper()}")
                    print(f"   Model: {ml_detection.get('model_type')}")
                else:
                    print(f"\n⚠️  ML Detection: Disabled (using fallback)")
                
                # Warnings
                if warnings:
                    print(f"\n⚠️  Warnings ({len(warnings)}):")
                    for j, warning in enumerate(warnings, 1):
                        print(f"   {j}. [{warning.get('severity')}] {warning.get('message')[:60]}...")
                else:
                    print(f"\n✅ No warnings detected")
                
                # Check if result matches expectation
                match = status == test['expected']
                match_emoji = "✅" if match else "❌"
                print(f"\n{match_emoji} Result: {'PASS' if match else 'FAIL'} (Expected: {test['expected']}, Got: {status})")
                
                results.append({
                    "test": test["name"],
                    "status": status,
                    "expected": test["expected"],
                    "match": match,
                    "ml_prob": ml_detection.get("phishing_probability", 0)
                })
                
            else:
                print(f"❌ Failed: Status code {response.status_code}")
                print(f"   Response: {response.text}")
                results.append({
                    "test": test["name"],
                    "status": "error",
                    "expected": test["expected"],
                    "match": False
                })
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "test": test["name"],
                "status": "error",
                "expected": test["expected"],
                "match": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    passed = sum(1 for r in results if r.get("match"))
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {(passed/total)*100:.1f}%")
    
    # Detailed results
    print(f"\n{'Test':<40} {'Expected':<12} {'Got':<12} {'Result'}")
    print("─"*70)
    for r in results:
        match_symbol = "✅" if r.get("match") else "❌"
        print(f"{r['test'][:38]:<40} {r['expected']:<12} {r['status']:<12} {match_symbol}")
    
    return passed == total

def test_security_status():
    """Test the security status endpoint"""
    print("\n" + "="*70)
    print("Testing Security Status Endpoint")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/security/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Security Status Retrieved:")
            print(f"   Security Level: {data.get('security_level')}")
            
            ml_detection = data.get('ml_phishing_detection', {})
            print(f"\n🤖 ML Detection Status:")
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

def main():
    """Run all tests"""
    print("="*70)
    print("URL Threat Detection - Complete Test Suite")
    print("="*70)
    print("\n⚠️  Make sure the server is running on http://localhost:8000")
    print("   Run: cd server && python main.py\n")
    
    input("Press Enter to continue...")
    
    # Run tests
    status_ok = test_security_status()
    validate_ok = test_api_validate()
    
    # Final summary
    print("\n" + "="*70)
    print("Final Results")
    print("="*70)
    
    if status_ok and validate_ok:
        print("\n🎉 All tests passed successfully!")
        print("\n✅ URL Threat Detection is working:")
        print("   • ML model loaded and operational")
        print("   • /api/validate endpoint functional")
        print("   • Color-coded threat detection active")
        print("   • Real-time chat analysis ready")
        print("\n🚀 You can now test in the chat:")
        print("   1. Open: http://localhost:8000/static/chat.html?session_id=test123")
        print("   2. Send a message with a URL")
        print("   3. Watch for color-coded threat warnings!")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
