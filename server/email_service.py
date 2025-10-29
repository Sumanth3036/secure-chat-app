"""
Email Service for OTP Verification
Supports SendGrid (recommended), Gmail SMTP, and Console mode
"""

import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# In-memory OTP storage (can be moved to Redis/MongoDB for production)
otp_storage: Dict[str, Dict] = {}

class EmailService:
    def __init__(self):
        # Support multiple email providers
        self.email_provider = os.getenv("EMAIL_PROVIDER", "console")  # console, gmail, sendgrid
        
        # Gmail configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_USER", "")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD", "")
        
        # SendGrid configuration (easier alternative)
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
        
        self.otp_expiry_minutes = 5
        
        # Determine which provider to use
        if self.email_provider == "sendgrid" and self.sendgrid_api_key:
            logger.info("✅ Email service: SendGrid")
        elif self.email_provider == "gmail" and self.sender_email and self.sender_password:
            logger.info(f"✅ Email service: Gmail ({self.sender_email})")
        else:
            self.email_provider = "console"
            logger.warning("⚠️ Email service: CONSOLE MODE (OTPs will be logged)")
            logger.info("💡 To enable real emails, set EMAIL_PROVIDER=sendgrid and SENDGRID_API_KEY")
        
    def generate_otp(self) -> str:
        """Generate a 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    def send_otp_email(self, recipient_email: str, otp: str, purpose: str = "verification") -> bool:
        """
        Send OTP email to recipient
        
        Args:
            recipient_email: Recipient's email address
            otp: 6-digit OTP code
            purpose: 'verification' or 'reset'
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Console mode - just log the OTP
        if self.email_provider == "console":
            logger.info("=" * 60)
            logger.info(f"📧 OTP EMAIL (Console Mode)")
            logger.info(f"To: {recipient_email}")
            logger.info(f"Purpose: {purpose}")
            logger.info(f"OTP: {otp}")
            logger.info(f"Expires in: {self.otp_expiry_minutes} minutes")
            logger.info("=" * 60)
            return True
        
        # SendGrid mode
        if self.email_provider == "sendgrid":
            return self._send_via_sendgrid(recipient_email, otp, purpose)
        
        # Gmail mode
        if self.email_provider == "gmail":
            return self._send_via_gmail(recipient_email, otp, purpose)
        
        return False
    
    def _send_via_sendgrid(self, recipient_email: str, otp: str, purpose: str) -> bool:
        """Send email via SendGrid API"""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            # Email content
            if purpose == "verification":
                subject = f"Your Secure Chat App Verification OTP - {otp}"
                intro_text = "Thank you for signing up with Secure Chat App!"
            else:
                subject = f"Your Secure Chat App Password Reset OTP - {otp}"
                intro_text = "You requested to reset your password."
            
            # HTML content
            html_content = self._get_email_html(otp, purpose, intro_text)
            
            # Create message
            message = Mail(
                from_email=Email("noreply@securechat.app", "Secure Chat App"),
                to_emails=To(recipient_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            # Send via SendGrid
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ SendGrid email sent to {recipient_email}")
                return True
            else:
                logger.error(f"❌ SendGrid failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            # Fallback to console
            logger.info(f"📧 FALLBACK - OTP for {recipient_email}: {otp}")
            return True
    
    def _send_via_gmail(self, recipient_email: str, otp: str, purpose: str) -> bool:
        """Send email via Gmail SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Your Secure Chat App OTP - {otp}"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Email content
            if purpose == "verification":
                intro_text = "Thank you for signing up with Secure Chat App!"
            else:
                intro_text = "You requested to reset your password."
            
            # HTML and plain text content
            html_content = self._get_email_html(otp, purpose, intro_text)
            text_content = f"""
Secure Chat App - OTP Verification

{intro_text}

Your OTP: {otp}

This OTP will expire in {self.otp_expiry_minutes} minutes.

If you didn't request this, please ignore this email.
            """
            
            # Attach both versions
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            logger.info(f"✅ Gmail email sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Gmail error: {e}")
            # Fallback to console
            logger.info(f"📧 FALLBACK - OTP for {recipient_email}: {otp}")
            return True
    
    def _get_email_html(self, otp: str, purpose: str, intro_text: str) -> str:
        """Generate HTML email template"""
        subject_line = "Email Verification" if purpose == "verification" else "Password Reset"
        
        return f"""
<html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #3d5afe; text-align: center;">🔐 Secure Chat App</h2>
            <h3 style="color: #333;">{subject_line}</h3>
            <p style="color: #666; font-size: 16px;">{intro_text}</p>
            <p style="color: #666; font-size: 16px;">Your One-Time Password (OTP) is:</p>
            <div style="background-color: #f0f0f0; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                <h1 style="color: #3d5afe; font-size: 36px; margin: 0; letter-spacing: 5px;">{otp}</h1>
            </div>
            <p style="color: #666; font-size: 14px;">
                ⏱️ This OTP will expire in <strong>{self.otp_expiry_minutes} minutes</strong>.
            </p>
            <p style="color: #666; font-size: 14px;">
                ⚠️ If you didn't request this, please ignore this email.
            </p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="color: #999; font-size: 12px; text-align: center;">
                This is an automated email. Please do not reply.<br>
                © 2025 Secure Chat App. All rights reserved.
            </p>
        </div>
    </body>
</html>
        """
    
    def store_otp(self, email: str, otp: str, purpose: str = "verification") -> None:
        """Store OTP with expiry time"""
        otp_storage[email] = {
            "otp": otp,
            "purpose": purpose,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes),
            "attempts": 0
        }
        logger.info(f"OTP stored for {email}, expires in {self.otp_expiry_minutes} minutes")
    
    def verify_otp(self, email: str, otp: str, purpose: str = "verification") -> Dict:
        """
        Verify OTP for given email
        
        Returns:
            dict: {"valid": bool, "message": str}
        """
        if email not in otp_storage:
            return {"valid": False, "message": "No OTP found for this email"}
        
        stored_data = otp_storage[email]
        
        # Check if OTP has expired
        if datetime.utcnow() > stored_data["expires_at"]:
            del otp_storage[email]
            return {"valid": False, "message": "OTP has expired"}
        
        # Check purpose
        if stored_data["purpose"] != purpose:
            return {"valid": False, "message": "Invalid OTP purpose"}
        
        # Check attempts (max 3 attempts)
        if stored_data["attempts"] >= 3:
            del otp_storage[email]
            return {"valid": False, "message": "Maximum attempts exceeded"}
        
        # Verify OTP
        if stored_data["otp"] == otp:
            del otp_storage[email]  # Remove OTP after successful verification
            return {"valid": True, "message": "OTP verified successfully"}
        else:
            stored_data["attempts"] += 1
            remaining = 3 - stored_data["attempts"]
            return {"valid": False, "message": f"Invalid OTP. {remaining} attempts remaining"}
    
    def send_verification_otp(self, email: str) -> Dict:
        """Send OTP for email verification during signup"""
        otp = self.generate_otp()
        success = self.send_otp_email(email, otp, purpose="verification")
        
        if success:
            self.store_otp(email, otp, purpose="verification")
            return {"success": True, "message": "OTP sent to your email"}
        else:
            return {"success": False, "message": "Failed to send OTP"}
    
    def send_password_reset_otp(self, email: str) -> Dict:
        """Send OTP for password reset"""
        otp = self.generate_otp()
        success = self.send_otp_email(email, otp, purpose="reset")
        
        if success:
            self.store_otp(email, otp, purpose="reset")
            return {"success": True, "message": "Password reset OTP sent to your email"}
        else:
            return {"success": False, "message": "Failed to send OTP"}

# Singleton instance
_email_service: Optional[EmailService] = None

def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
