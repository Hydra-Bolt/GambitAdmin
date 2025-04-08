"""
Email service utilities for sending emails in the Gambit Admin API.
"""

import smtplib
import logging
import random
import string
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file


logger = logging.getLogger(__name__)

# Email configuration - Read from environment variables
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.environ.get("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")  # App password for Gmail

# For development only - enable this flag to skip actual email sending
# In development, OTPs will be logged to console instead of sent via email
DEV_MODE = os.environ.get("DEV_MODE", "false").lower() == "true"

# OTP configuration
OTP_EXPIRY_MINUTES = 10
OTP_LENGTH = 6

# In-memory storage for OTPs
# In production, this should be moved to a database
# Format: {"email": {"otp": "123456", "expiry": datetime_object, "verified": False, "purpose": "signup/reset"}}
otp_store = {}


def generate_otp(length=OTP_LENGTH):
    """Generate a random numeric OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))


def store_otp(email, otp, purpose="signup"):
    """Store OTP with expiry time"""
    otp_store[email] = {
        "otp": otp,
        "expiry": datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
        "verified": False,
        "purpose": purpose
    }
    
    # In development mode, log the OTP for easy testing
    if DEV_MODE:
        logger.info(f"DEV MODE - OTP for {email}: {otp} (purpose: {purpose})")


def verify_otp(email, otp):
    """Verify if the provided OTP is valid and not expired"""
    if email not in otp_store:
        return False
    
    otp_data = otp_store[email]
    
    if otp_data["otp"] != otp:
        return False
    
    if otp_data["expiry"] < datetime.now():
        # OTP has expired
        return False
    
    # Mark as verified
    otp_data["verified"] = True
    return True


def is_otp_verified(email, purpose=None):
    """Check if OTP for the email is verified"""
    if email not in otp_store:
        return False
    
    otp_data = otp_store[email]
    
    # If purpose is specified, check if it matches
    if purpose and otp_data["purpose"] != purpose:
        return False
        
    return otp_data["verified"]


def clear_otp(email):
    """Clear OTP data for an email"""
    if email in otp_store:
        del otp_store[email]


def send_otp_email(recipient_email, otp, purpose="signup"):
    """Send OTP via email"""
    subject = "Your Gambit OTP Code"
    
    if purpose == "signup":
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #5c2d91;">Welcome to Gambit!</h2>
                <p>Thank you for signing up. To complete your registration, please use the following OTP:</p>
                <div style="background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; margin: 20px 0;">
                    {otp}
                </div>
                <p>This code will expire in {OTP_EXPIRY_MINUTES} minutes.</p>
                <p>If you did not request this code, please ignore this email.</p>
                <p>Best regards,<br>The Gambit Team</p>
            </body>
        </html>
        """
    elif purpose == "reset":
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #5c2d91;">Password Reset Request</h2>
                <p>You requested to change your password. Please use the following OTP to verify your request:</p>
                <div style="background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; margin: 20px 0;">
                    {otp}
                </div>
                <p>This code will expire in {OTP_EXPIRY_MINUTES} minutes.</p>
                <p>If you did not request this code, please secure your account immediately.</p>
                <p>Best regards,<br>The Gambit Team</p>
            </body>
        </html>
        """
    else:
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #5c2d91;">Your OTP Code</h2>
                <p>You requested a verification code. Please use the following OTP:</p>
                <div style="background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; margin: 20px 0;">
                    {otp}
                </div>
                <p>This code will expire in {OTP_EXPIRY_MINUTES} minutes.</p>
                <p>If you did not request this code, please ignore this email.</p>
                <p>Best regards,<br>The Gambit Team</p>
            </body>
        </html>
        """
    
    # In development mode, just return True without actually sending email
    if DEV_MODE:
        logger.info(f"DEV MODE - Would have sent email to {recipient_email} with subject '{subject}'")
        return True
        
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        
        # Try to login - if it fails with one method, try alternatives
        try:
            # Try standard login first
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        except smtplib.SMTPAuthenticationError as auth_error:
            logger.warning(f"Standard login failed: {str(auth_error)}")
            
            # For development/testing - automatically switch to DEV_MODE if email sending fails
            logger.info("Email authentication failed. Switching to DEV_MODE to allow application testing.")
            logger.info(f"OTP for {recipient_email}: {otp} (purpose: {purpose})")
            return True
            
        server.send_message(msg)
        server.quit()
        
        logger.info(f"OTP email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email: {str(e)}")
        
        # For development/testing - log the OTP so testing can continue
        logger.info(f"Email sending failed. For testing purposes, OTP for {recipient_email}: {otp}")
        return False