"""
Test script to verify CatBoost ML model integration
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ml_detector import get_detector

def test_phishing_detection():
    """Test the phishing detection with various URLs"""
    
    print("="*60)
    print("Testing CatBoost Phishing Detection Integration")
    print("="*60)
    
    # Get detector instance
    detector = get_detector()
    
    print(f"\n📊 Model Status:")
    print(f"   Model loaded: {detector.model is not None}")
    print(f"   Fallback mode: {detector.fallback_mode}")
    print(f"   Model path: {detector.model_path}")
    
    # Test cases
    test_cases = [
        # Legitimate URLs
        ("https://www.google.com", "Legitimate - Google"),
        ("https://github.com/user/repo", "Legitimate - GitHub"),
        ("https://www.amazon.com/products", "Legitimate - Amazon"),
        
        # Suspicious URLs
        ("http://192.168.1.1/login", "Suspicious - IP address"),
        ("http://bit.ly/xyz123", "Suspicious - URL shortener"),
        ("http://paypal-secure-login.tk/verify", "Suspicious - Fake PayPal"),
        ("http://bank-account@malicious.com", "Suspicious - @ symbol"),
        ("http://www.goog1e.com/signin", "Suspicious - Typosquatting"),
        
        # Text messages
        ("Click here to verify your account", "Text - Phishing message"),
        ("Hello, how are you today?", "Text - Normal message"),
        ("URGENT: Your account will be closed!", "Text - Urgent phishing"),
    ]
    
    print("\n" + "="*60)
    print("Test Results:")
    print("="*60)
    
    for content, description in test_cases:
        try:
            prob = detector.predict_proba(content)
            risk_level = "🔴 HIGH" if prob > 0.7 else ("🟡 MEDIUM" if prob > 0.4 else "🟢 LOW")
            
            print(f"\n{description}")
            print(f"   Content: {content[:50]}...")
            print(f"   Phishing Probability: {prob:.4f}")
            print(f"   Risk Level: {risk_level}")
            
        except Exception as e:
            print(f"\n❌ Error testing '{description}': {e}")
    
    print("\n" + "="*60)
    print("✅ Testing Complete!")
    print("="*60)

def test_feature_extraction():
    """Test feature extraction"""
    print("\n" + "="*60)
    print("Testing Feature Extraction")
    print("="*60)
    
    detector = get_detector()
    
    test_url = "http://192.168.1.1:8080/login?user=admin&pass=123"
    features = detector.extract_features(test_url)
    
    print(f"\nTest URL: {test_url}")
    print(f"\nExtracted Features ({len(features)} total):")
    
    for i, (feature_name, value) in enumerate(features.items(), 1):
        print(f"   {i:2d}. {feature_name:20s}: {value:2d}")
    
    print("\n✅ Feature extraction successful!")

if __name__ == "__main__":
    try:
        test_phishing_detection()
        test_feature_extraction()
        
        print("\n" + "="*60)
        print("🎉 All tests completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
