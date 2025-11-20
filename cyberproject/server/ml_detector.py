import os
import re
import math
import logging
from typing import Optional, Dict, Any

import joblib

logger = logging.getLogger(__name__)


class CatBoostPhishingDetector:
    """
    Loads a CatBoost classifier from a pickle and provides a predict_proba interface
    on raw content (text/URL). Uses the trained CatBoost model for phishing detection.

    The model expects 30 features extracted from URLs/text content.
    Falls back to rule-based detection if model is unavailable.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.getenv(
            "PHISHING_MODEL_PATH",
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "mlmodel",
                "mlmodelsperformance",
                "catboost_phishing.pkl",
            ),
        )
        self.model = None
        self.fallback_mode = False  # Will be set to True if model fails to load
        self.feature_names = [
            'UsingIP', 'LongURL', 'ShortURL', 'Symbol@', 'Redirecting//',
            'PrefixSuffix-', 'SubDomains', 'HTTPS', 'DomainRegLen', 'Favicon',
            'NonStdPort', 'HTTPSDomainURL', 'RequestURL', 'AnchorURL',
            'LinksInScriptTags', 'ServerFormHandler', 'InfoEmail', 'AbnormalURL',
            'WebsiteForwarding', 'StatusBarCust', 'DisableRightClick',
            'UsingPopupWindow', 'IframeRedirection', 'AgeofDomain', 'DNSRecording',
            'WebsiteTraffic', 'PageRank', 'GoogleIndex', 'LinksPointingToPage',
            'StatsReport'
        ]
        self._load_model()

    def _load_model(self) -> None:
        try:
            if os.path.isfile(self.model_path):
                self.model = joblib.load(self.model_path)
                self.fallback_mode = False
                logger.info(f"✅ CatBoost model loaded successfully from: {self.model_path}")
            else:
                self.fallback_mode = True
                logger.warning(
                    f"⚠️ CatBoost model file not found at {self.model_path}. Falling back to rule-based detection."
                )
        except Exception as exc:
            self.fallback_mode = True
            logger.warning(f"⚠️ Failed to load CatBoost model: {exc}. Falling back to rule-based detection.")
            self.model = None

    @staticmethod
    def _is_url(text: str) -> bool:
        return bool(re.search(r"https?://", text, re.IGNORECASE))

    @staticmethod
    def _count(pattern: str, text: str) -> int:
        return len(re.findall(pattern, text))

    def extract_features(self, content: str) -> Dict[str, int]:
        """
        Extract 30 features from URL/text content to match the training dataset.
        Returns a dictionary with feature names as keys and values as -1, 0, or 1.
        
        Features are heuristic approximations of the original dataset features.
        """
        text = content.strip()
        lower = text.lower()
        length = len(text)
        
        # Helper function to convert boolean to -1/1
        def bool_to_feature(condition):
            return 1 if condition else -1
        
        # Extract features (approximations based on URL characteristics)
        features = {
            'UsingIP': bool_to_feature(bool(re.search(r'https?://\d+\.\d+\.\d+\.\d+', lower))),
            'LongURL': 1 if length > 75 else (-1 if length > 54 else 0),
            'ShortURL': bool_to_feature(bool(re.search(r'bit\.ly|tinyurl|goo\.gl|t\.co|ow\.ly', lower))),
            'Symbol@': bool_to_feature('@' in text),
            'Redirecting//': bool_to_feature(text.count('//') > 1),
            'PrefixSuffix-': bool_to_feature('-' in text.split('/')[0] if '/' in text else '-' in text),
            'SubDomains': 1 if text.count('.') > 3 else (0 if text.count('.') > 1 else -1),
            'HTTPS': bool_to_feature(lower.startswith('https://')),
            'DomainRegLen': 1 if 6 <= length <= 20 else -1,
            'Favicon': -1,  # Cannot determine from text
            'NonStdPort': bool_to_feature(bool(re.search(r':\d{2,5}/', text))),
            'HTTPSDomainURL': bool_to_feature('https' in lower),
            'RequestURL': -1,  # Cannot determine from text alone
            'AnchorURL': 0,  # Neutral default
            'LinksInScriptTags': 0,  # Cannot determine from text
            'ServerFormHandler': -1,  # Cannot determine from text
            'InfoEmail': bool_to_feature(bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))),
            'AbnormalURL': bool_to_feature(bool(re.search(r'[^a-zA-Z0-9./:?=&_-]', text))),
            'WebsiteForwarding': 0,  # Cannot determine from text
            'StatusBarCust': 1,  # Default assumption
            'DisableRightClick': 1,  # Default assumption
            'UsingPopupWindow': 1,  # Default assumption
            'IframeRedirection': 1,  # Default assumption
            'AgeofDomain': -1,  # Cannot determine from text
            'DNSRecording': -1,  # Cannot determine from text
            'WebsiteTraffic': 0,  # Cannot determine from text
            'PageRank': -1,  # Cannot determine from text
            'GoogleIndex': 1,  # Default assumption
            'LinksPointingToPage': 0,  # Cannot determine from text
            'StatsReport': 1  # Default assumption
        }
        
        # Additional heuristics for suspicious patterns
        if bool(re.search(r'\.(tk|ml|ga|cf|gq)(/|$)', lower)):
            features['DomainRegLen'] = -1
            features['PageRank'] = -1
            
        return features

    def predict_proba(self, content: str) -> Optional[float]:
        """
        Returns probability of phishing (higher value = more likely phishing).
        Uses trained CatBoost model if available, otherwise falls back to rule-based detection.
        
        Returns:
            float: Probability score between 0.0 and 1.0
        """
        if self.model is None or self.fallback_mode:
            # Fallback to rule-based detection
            return self._rule_based_detection(content)
            
        try:
            # Extract features
            feats = self.extract_features(content)
            
            # Create feature vector in the correct order
            X = [[feats[feature_name] for feature_name in self.feature_names]]
            
            # Get prediction from CatBoost model
            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba(X)[0]
                # CatBoost returns probabilities for each class
                # In the training data: -1 = legitimate (benign), 1 = phishing
                # proba[0] = probability of class -1 (legitimate)
                # proba[1] = probability of class 1 (phishing)
                if len(proba) == 2:
                    # Return probability of phishing (class 1)
                    phishing_prob = float(proba[1])
                else:
                    phishing_prob = float(proba[0])
                
                logger.debug(f"CatBoost prediction: {phishing_prob:.4f} for content: {content[:50]}...")
                return phishing_prob
            else:
                # Fallback to binary prediction
                pred = self.model.predict(X)[0]
                # Convert -1/1 to 0.0/1.0
                return 1.0 if pred == 1 else 0.0
                
        except Exception as exc:
            logger.warning(f"ML prediction failed: {exc}. Falling back to rule-based detection.")
            return self._rule_based_detection(content)
            
    def _rule_based_detection(self, content: str) -> float:
        """
        Simple rule-based detection as fallback when ML model is unavailable.
        Returns a probability score between 0.0 and 1.0.
        """
        text = content.lower().strip()
        score = 0.0
        
        # Check for suspicious patterns
        patterns = [
            r'https?://[^\s]*\.(tk|ml|ga|cf|gq)(/|$)',  # Suspicious TLDs
            r'https?://[^\s]*\.(bit\.ly|tinyurl|goo\.gl|t\.co)',  # URL shorteners
            r'https?://\d+\.\d+\.\d+\.\d+',  # IP addresses in URLs
            r'password|login|signin|bank|account|update|verify|confirm',  # Suspicious keywords
            r'urgent|alert|warning|attention|important',  # Urgency keywords
            r'bitcoin|crypto|wallet|transfer|money',  # Financial keywords
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                score += 0.2  # Increase score for each matched pattern
        
        # Cap the score at 1.0
        return min(score, 1.0)


# Singleton-like accessor
_detector: Optional[CatBoostPhishingDetector] = None


def get_detector() -> CatBoostPhishingDetector:
    global _detector
    if _detector is None:
        _detector = CatBoostPhishingDetector()
    return _detector



