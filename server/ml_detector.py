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
    on raw content (text/URL). Includes a simple, deterministic feature extractor.

    IMPORTANT: The feature extractor must match what was used during training.
    If your training used a different set/order of features, update `extract_features`
    accordingly to ensure consistency.
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
        self.fallback_mode = True  # Set fallback mode to True by default
        self._load_model()

    def _load_model(self) -> None:
        try:
            if os.path.isfile(self.model_path):
                self.model = joblib.load(self.model_path)
                self.fallback_mode = False  # Model loaded successfully
                logger.info(f"CatBoost model loaded from: {self.model_path}")
                logger.info("ML phishing detection enabled")
            else:
                logger.warning(
                    f"CatBoost model file not found at {self.model_path}. Falling back to rules."
                )
        except Exception as exc:
            logger.warning(f"Failed to load CatBoost model: {exc}. Falling back to rules.")
            self.model = None

    @staticmethod
    def _is_url(text: str) -> bool:
        return bool(re.search(r"https?://", text, re.IGNORECASE))

    @staticmethod
    def _count(pattern: str, text: str) -> int:
        return len(re.findall(pattern, text))

    def extract_features(self, content: str) -> Dict[str, float]:
        """
        Heuristic feature extractor for URLs/text. Replace/extend to match training.
        """
        text = content.strip()
        lower = text.lower()
        length = len(text)
        num_digits = sum(ch.isdigit() for ch in text)
        num_letters = sum(ch.isalpha() for ch in text)
        num_special = length - num_digits - num_letters
        num_dots = text.count(".")
        num_hyphens = text.count("-")
        at_present = 1.0 if "@" in text else 0.0
        url_like = 1.0 if self._is_url(text) else 0.0
        num_slashes = text.count("/")
        num_params = text.count("?") + text.count("&") + text.count("=")
        has_https = 1.0 if lower.startswith("https://") else 0.0
        tld_suspicious = 1.0 if re.search(r"\.(tk|ml|ga|cf|gq)(/|$)", lower) else 0.0
        has_ip = 1.0 if re.search(r"https?://\d+\.\d+\.\d+\.\d+", lower) else 0.0
        entropy = 0.0
        if length > 0:
            from collections import Counter

            counts = Counter(lower)
            probs = [c / float(length) for c in counts.values()]
            entropy = -sum(p * math.log(p, 2) for p in probs if p > 0)

        return {
            "length": float(length),
            "num_digits": float(num_digits),
            "num_letters": float(num_letters),
            "num_special": float(num_special),
            "num_dots": float(num_dots),
            "num_hyphens": float(num_hyphens),
            "num_slashes": float(num_slashes),
            "num_params": float(num_params),
            "at_present": at_present,
            "url_like": url_like,
            "has_https": has_https,
            "tld_suspicious": tld_suspicious,
            "has_ip": has_ip,
            "entropy": float(entropy),
        }

    def predict_proba(self, content: str) -> Optional[float]:
        """
        Returns probability of phishing (1.0 = phishing) or None if model unavailable.
        """
        if self.model is None:
            return None
        try:
            feats = self.extract_features(content)
            # Preserve a stable column order; update to match training order
            columns = [
                "length",
                "num_digits",
                "num_letters",
                "num_special",
                "num_dots",
                "num_hyphens",
                "num_slashes",
                "num_params",
                "at_present",
                "url_like",
                "has_https",
                "tld_suspicious",
                "has_ip",
                "entropy",
            ]
            X = [[feats[c] for c in columns]]
            # CatBoost and many sklearn APIs expose predict_proba
            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba(X)[0]
                # Binary: [p(benign), p(phishing)]
                phishing_p = float(proba[1]) if isinstance(proba, (list, tuple)) else float(proba)
                return phishing_p
            # Fallback: raw predict mapped to {0,1}
            pred = self.model.predict(X)
            try:
                return float(pred[0])
            except Exception:
                return float(pred)
        except Exception as exc:
            logger.warning(f"ML prediction failed: {exc}. Falling back to rules.")
            return None


# Singleton-like accessor
_detector: Optional[CatBoostPhishingDetector] = None


def get_detector() -> CatBoostPhishingDetector:
    global _detector
    if _detector is None:
        _detector = CatBoostPhishingDetector()
    return _detector



