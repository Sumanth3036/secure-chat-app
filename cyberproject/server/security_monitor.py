import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Set
from dataclasses import dataclass
from collections import defaultdict
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityWarning:
    user_email: str
    session_id: str
    warning_type: str
    message: str
    timestamp: datetime
    severity: str  # 'low', 'medium', 'high', 'critical'

class SecurityMonitor:
    def __init__(self):
        # Track warnings per user per session
        self.user_warnings: Dict[str, Dict[str, List[SecurityWarning]]] = defaultdict(lambda: defaultdict(list))
        
        # Track suspicious patterns
        self.suspicious_urls: Set[str] = set()
        self.suspicious_domains: Set[str] = set()
        
        # Rate limiting
        self.message_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.last_message_time: Dict[str, Dict[str, datetime]] = defaultdict(lambda: defaultdict(lambda: datetime.min))
        
        # ML phishing detection configuration
        self.enable_ml_detection = os.getenv("ENABLE_ML_PHISHING", "true").lower() == "true"
        try:
            from ml_detector import get_detector
            self.ml_detector = get_detector() if self.enable_ml_detection else None
            logger.info("ML detector initialized successfully in fallback mode")
        except Exception as e:
            logger.warning(f"Failed to initialize ML detector: {e}. Using rule-based detection only.")
            self.ml_detector = None

        # Threshold for ML phishing probability (0..1)
        try:
            self.ml_phishing_threshold = float(os.getenv("ML_PHISHING_THRESHOLD", "0.75"))
        except Exception:
            self.ml_phishing_threshold = 0.75

        # Phishing detection patterns (rules fallback / complement)
        self.phishing_patterns = [
            r'https?://[^\s]*\.(tk|ml|ga|cf|gq)',  # Suspicious TLDs
            r'https?://[^\s]*\.(bit\.ly|tinyurl|goo\.gl|t\.co)',  # URL shorteners
            r'https?://[^\s]*\.(paypal|bank|secure|login|verify)',  # Phishing keywords
            r'https?://[^\s]*\.(microsoft|google|apple|amazon)',  # Brand impersonation
            r'https?://[^\s]*\.(crypto|bitcoin|wallet|exchange)',  # Crypto scams
            r'https?://[^\s]*\.(free|win|prize|lottery|gift)',  # Scam keywords
        ]
        
        # Malicious content patterns
        self.malicious_patterns = [
            r'<script[^>]*>',  # Script injection
            r'javascript:',  # JavaScript protocol
            r'on\w+\s*=',  # Event handlers
            r'<iframe[^>]*>',  # Iframe injection
            r'<object[^>]*>',  # Object injection
            r'<embed[^>]*>',  # Embed injection
            r'<form[^>]*>',  # Form injection
            r'<input[^>]*>',  # Input injection
            r'<textarea[^>]*>',  # Textarea injection
            r'<select[^>]*>',  # Select injection
            r'<button[^>]*>',  # Button injection
            r'<link[^>]*>',  # Link injection
            r'<meta[^>]*>',  # Meta injection
            r'<style[^>]*>',  # Style injection
            r'<title[^>]*>',  # Title injection
            r'<base[^>]*>',  # Base injection
            r'<bgsound[^>]*>',  # Bgsound injection
            r'<xmp[^>]*>',  # Xmp injection
            r'<plaintext[^>]*>',  # Plaintext injection
            r'<listing[^>]*>',  # Listing injection
            r'<marquee[^>]*>',  # Marquee injection
            r'<applet[^>]*>',  # Applet injection
            r'<param[^>]*>',  # Param injection
            r'<source[^>]*>',  # Source injection
            r'<track[^>]*>',  # Track injection
            r'<video[^>]*>',  # Video injection
            r'<audio[^>]*>',  # Audio injection
            r'<canvas[^>]*>',  # Canvas injection
            r'<svg[^>]*>',  # Svg injection
            r'<math[^>]*>',  # Math injection
            r'<details[^>]*>',  # Details injection
            r'<dialog[^>]*>',  # Dialog injection
            r'<menu[^>]*>',  # Menu injection
            r'<menuitem[^>]*>',  # Menuitem injection
            r'<summary[^>]*>',  # Summary injection
            r'<content[^>]*>',  # Content injection
            r'<element[^>]*>',  # Element injection
            r'<shadow[^>]*>',  # Shadow injection
            r'<template[^>]*>',  # Template injection
            r'<slot[^>]*>',  # Slot injection
            r'<picture[^>]*>',  # Picture injection
            r'<figure[^>]*>',  # Figure injection
            r'<figcaption[^>]*>',  # Figcaption injection
            r'<main[^>]*>',  # Main injection
            r'<section[^>]*>',  # Section injection
            r'<article[^>]*>',  # Article injection
            r'<aside[^>]*>',  # Aside injection
            r'<header[^>]*>',  # Header injection
            r'<footer[^>]*>',  # Footer injection
            r'<nav[^>]*>',  # Nav injection
            r'<address[^>]*>',  # Address injection
            r'<blockquote[^>]*>',  # Blockquote injection
            r'<dd[^>]*>',  # Dd injection
            r'<div[^>]*>',  # Div injection
            r'<dl[^>]*>',  # Dl injection
            r'<dt[^>]*>',  # Dt injection
            r'<fieldset[^>]*>',  # Fieldset injection
            r'<figcaption[^>]*>',  # Figcaption injection
            r'<figure[^>]*>',  # Figure injection
            r'<hr[^>]*>',  # Hr injection
            r'<li[^>]*>',  # Li injection
            r'<ol[^>]*>',  # Ol injection
            r'<p[^>]*>',  # P injection
            r'<pre[^>]*>',  # Pre injection
            r'<ul[^>]*>',  # Ul injection
            r'<a[^>]*>',  # Anchor injection
            r'<abbr[^>]*>',  # Abbr injection
            r'<acronym[^>]*>',  # Acronym injection
            r'<b[^>]*>',  # Bold injection
            r'<bdi[^>]*>',  # Bdi injection
            r'<bdo[^>]*>',  # Bdo injection
            r'<big[^>]*>',  # Big injection
            r'<br[^>]*>',  # Br injection
            r'<cite[^>]*>',  # Cite injection
            r'<code[^>]*>',  # Code injection
            r'<del[^>]*>',  # Del injection
            r'<dfn[^>]*>',  # Dfn injection
            r'<em[^>]*>',  # Em injection
            r'<i[^>]*>',  # Italic injection
            r'<ins[^>]*>',  # Ins injection
            r'<kbd[^>]*>',  # Kbd injection
            r'<mark[^>]*>',  # Mark injection
            r'<q[^>]*>',  # Quote injection
            r'<s[^>]*>',  # Strike injection
            r'<samp[^>]*>',  # Samp injection
            r'<small[^>]*>',  # Small injection
            r'<span[^>]*>',  # Span injection
            r'<strong[^>]*>',  # Strong injection
            r'<sub[^>]*>',  # Sub injection
            r'<sup[^>]*>',  # Sup injection
            r'<time[^>]*>',  # Time injection
            r'<tt[^>]*>',  # Tt injection
            r'<u[^>]*>',  # Underline injection
            r'<var[^>]*>',  # Var injection
            r'<wbr[^>]*>',  # Wbr injection
        ]
        
        # Spam patterns
        self.spam_patterns = [
            r'\b(viagra|cialis|levitra)\b',  # Drug spam
            r'\b(casino|poker|bet|gambling)\b',  # Gambling spam
            r'\b(loan|credit|debt|mortgage)\b',  # Financial spam
            r'\b(weight\s*loss|diet|supplement)\b',  # Health spam
            r'\b(make\s*money|earn\s*cash|get\s*rich)\b',  # Money spam
            r'\b(free\s*offer|limited\s*time|act\s*now)\b',  # Urgency spam
        ]
        
        # Rate limiting thresholds
        self.max_messages_per_minute = 30
        self.max_messages_per_hour = 500
        self.max_warnings_before_ban = 3
        
    def analyze_message(self, user_email: str, session_id: str, message: str) -> List[SecurityWarning]:
        """Analyze a message for security threats and return warnings"""
        warnings = []
        
        # ML-based phishing detection (probabilistic)
        phishing_warnings = []
        if self.ml_detector is not None:
            try:
                ml_score = self.ml_detector.predict_proba(message)  # 0..1
            except Exception:
                ml_score = None
            if ml_score is not None and ml_score >= self.ml_phishing_threshold:
                phishing_warnings.append(f"ML model flagged content as phishing with score {ml_score:.2f}")

        # Rules-based phishing detection (complement/fallback)
        rule_warnings = self._detect_phishing(message)
        phishing_warnings.extend(rule_warnings)
        for warning in phishing_warnings:
            warnings.append(SecurityWarning(
                user_email=user_email,
                session_id=session_id,
                warning_type="phishing_ml" if "ML model" in warning else "phishing_url",
                message=warning,
                timestamp=datetime.utcnow(),
                severity="high"
            ))
        
        # Check for malicious content
        malicious_warnings = self._detect_malicious_content(message)
        for warning in malicious_warnings:
            warnings.append(SecurityWarning(
                user_email=user_email,
                session_id=session_id,
                warning_type="malicious_content",
                message=warning,
                timestamp=datetime.utcnow(),
                severity="critical"
            ))
        
        # Check for spam
        spam_warnings = self._detect_spam(message)
        for warning in spam_warnings:
            warnings.append(SecurityWarning(
                user_email=user_email,
                session_id=session_id,
                warning_type="spam",
                message=warning,
                timestamp=datetime.utcnow(),
                severity="medium"
            ))
        
        # Check rate limiting
        rate_limit_warnings = self._check_rate_limiting(user_email, session_id)
        for warning in rate_limit_warnings:
            warnings.append(SecurityWarning(
                user_email=user_email,
                session_id=session_id,
                warning_type="rate_limit",
                message=warning,
                timestamp=datetime.utcnow(),
                severity="medium"
            ))
        
        return warnings
    
    def _detect_phishing(self, message: str) -> List[str]:
        """Detect phishing URLs in message"""
        warnings = []
        urls = re.findall(r'https?://[^\s]+', message.lower())
        
        for url in urls:
            for pattern in self.phishing_patterns:
                if re.search(pattern, url):
                    warnings.append(f"Potential phishing URL detected: {url}")
                    break
        
        return warnings
    
    def _detect_malicious_content(self, message: str) -> List[str]:
        """Detect malicious content (XSS, injection attempts)"""
        warnings = []
        
        for pattern in self.malicious_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                warnings.append(f"Malicious content detected: {pattern}")
        
        return warnings
    
    def _detect_spam(self, message: str) -> List[str]:
        """Detect spam patterns"""
        warnings = []
        
        for pattern in self.spam_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                warnings.append(f"Spam content detected: {pattern}")
        
        return warnings
    
    def _check_rate_limiting(self, user_email: str, session_id: str) -> List[str]:
        """Check if user is sending too many messages"""
        warnings = []
        now = datetime.utcnow()
        
        # Update message count
        self.message_counts[user_email][session_id] += 1
        
        # Check per-minute limit
        if now - self.last_message_time[user_email][session_id] < timedelta(minutes=1):
            if self.message_counts[user_email][session_id] > self.max_messages_per_minute:
                warnings.append(f"Rate limit exceeded: {self.message_counts[user_email][session_id]} messages in 1 minute")
        else:
            # Reset counter if more than 1 minute has passed
            self.message_counts[user_email][session_id] = 1
        
        self.last_message_time[user_email][session_id] = now
        
        return warnings
    
    def add_warning(self, warning: SecurityWarning):
        """Add a warning to the user's record"""
        self.user_warnings[warning.user_email][warning.session_id].append(warning)
        logger.warning(f"Security warning for {warning.user_email}: {warning.warning_type} - {warning.message}")
    
    def get_warning_count(self, user_email: str, session_id: str) -> int:
        """Get the number of warnings for a user in a session"""
        return len(self.user_warnings[user_email][session_id])
    
    def should_terminate_session(self, user_email: str, session_id: str) -> bool:
        """Check if session should be terminated due to too many warnings"""
        warning_count = self.get_warning_count(user_email, session_id)
        return warning_count >= self.max_warnings_before_ban
    
    def get_user_warnings(self, user_email: str, session_id: str) -> List[SecurityWarning]:
        """Get all warnings for a user in a session"""
        return self.user_warnings[user_email][session_id]
    
    def clear_warnings(self, user_email: str, session_id: str):
        """Clear warnings for a user in a session"""
        if user_email in self.user_warnings and session_id in self.user_warnings[user_email]:
            del self.user_warnings[user_email][session_id]
    
    def get_security_report(self, user_email: str, session_id: str) -> dict:
        """Get a security report for a user in a session"""
        warnings = self.get_user_warnings(user_email, session_id)
        warning_count = len(warnings)
        
        return {
            "user_email": user_email,
            "session_id": session_id,
            "warning_count": warning_count,
            "warnings": [
                {
                    "type": w.warning_type,
                    "message": w.message,
                    "severity": w.severity,
                    "timestamp": w.timestamp.isoformat()
                }
                for w in warnings
            ],
            "should_terminate": self.should_terminate_session(user_email, session_id),
            "max_warnings": self.max_warnings_before_ban
        }

# Global security monitor instance
security_monitor = SecurityMonitor()
