import os
import re
import logging
from typing import Optional, Dict
from pathlib import Path

import joblib

logger = logging.getLogger(__name__)

class CatBoostPhishingDetector:
    """
    Loads a CatBoost classifier from a pickle and provides a predict_proba interface.
    Falls back to rule-based detection if model file is missing or invalid.
    """

    def __init__(self, model_path: Optional[str] = None):
        if model_path:
            self.model_path = model_path
        elif os.getenv("PHISHING_MODEL_PATH"):
            self.model_path = os.getenv("PHISHING_MODEL_PATH")
        else:
            # Render-safe full absolute path → project_root/mlmodel/mlmodelsperformance/...
            BASE_DIR = Path(__file__).resolve().parent.parent
            self.model_path = BASE_DIR / "mlmodel" / "mlmodelsperformance" / "catboost_phishing.pkl"

        # Ensure absolute path
        self.model_path = str(Path(self.model_path).resolve())

        logger.info(f"Using ML model path: {self.model_path}")

        self.model = None
        self.fallback_mode = False
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

    def _load_model(self):
        try:
            path = Path(self.model_path)
            if path.is_file():
                logger.info(f"Loading CatBoost model from: {path}")
                self.model = joblib.load(path)
                # Validate model
                if not hasattr(self.model, "predict"):
                    raise ValueError("Invalid ML model loaded (missing predict method)")
                self.fallback_mode = False
                logger.info("CatBoost model loaded successfully")
                return
            # File missing
            logger.warning(f"Model not found at {path}. Switching to fallback detection.")
            self.fallback_mode = True
        except Exception as exc:
            logger.warning(f"Model load failed: {exc}. Using fallback mode.")
            self.model = None
            self.fallback_mode = True

    @staticmethod
    def _is_url(text: str) -> bool:
        return bool(re.search(r"https?://", text, re.IGNORECASE))

    @staticmethod
    def _count(pattern: str, text: str) -> int:
        return len(re.findall(pattern, text))

    def extract_features(self, content: str) -> Dict[str, int]:
        text = content.strip()
        lower = text.lower()
        length = len(text)

        def bool_to_feature(c): return 1 if c else -1

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
            'Favicon': -1,
            'NonStdPort': bool_to_feature(bool(re.search(r':\d{2,5}/', text))),
            'HTTPSDomainURL': bool_to_feature('https' in lower),
            'RequestURL': -1,
            'AnchorURL': 0,
            'LinksInScriptTags': 0,
            'ServerFormHandler': -1,
            'InfoEmail': bool_to_feature(bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))),
            'AbnormalURL': bool_to_feature(bool(re.search(r'[^a-zA-Z0-9./:?=&_-]', text))),
            'WebsiteForwarding': 0,
            'StatusBarCust': 1,
            'DisableRightClick': 1,
            'UsingPopupWindow': 1,
            'IframeRedirection': 1,
            'AgeofDomain': -1,
            'DNSRecording': -1,
            'WebsiteTraffic': 0,
            'PageRank': -1,
            'GoogleIndex': 1,
            'LinksPointingToPage': 0,
            'StatsReport': 1
        }

        if re.search(r'\.(tk|ml|ga|cf|gq)(/|$)', lower):
            features['DomainRegLen'] = -1
            features['PageRank'] = -1

        return features

    def predict_proba(self, content: str) -> float:
        """Returns probability of phishing (0.0–1.0)."""
        if self.model is None or self.fallback_mode:
            return self._rule_based_detection(content)

        try:
            feats = self.extract_features(content)
            X = [[feats[f] for f in self.feature_names]]

            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba(X)[0]
                return float(proba[1]) if len(proba) == 2 else float(proba[0])

            pred = self.model.predict(X)[0]
            return 1.0 if pred == 1 else 0.0

        except Exception as exc:
            logger.warning(f"Prediction failed: {exc}. Using fallback mode.")
            return self._rule_based_detection(content)

    def _rule_based_detection(self, content: str) -> float:
        text = content.lower().strip()
        score = 0.0

        patterns = [
            r'https?://[^\s]*\.(tk|ml|ga|cf|gq)(/|$)',
            r'https?://[^\s]*\.(bit\.ly|tinyurl|goo\.gl|t\.co)',
            r'https?://\d+\.\d+\.\d+\.\d+',
            r'password|login|signin|bank|account|update|verify|confirm',
            r'urgent|alert|warning|attention|important',
            r'bitcoin|crypto|wallet|transfer|money',
        ]

        for p in patterns:
            if re.search(p, text):
                score += 0.2

        return min(score, 1.0)

# Singleton
_detector: Optional[CatBoostPhishingDetector] = None

def get_detector():
    global _detector
    if _detector is None:
        _detector = CatBoostPhishingDetector()
    return _detector
