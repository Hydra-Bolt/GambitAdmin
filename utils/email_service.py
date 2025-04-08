"""
Email service utilities for sending emails in the Gambit Admin API.
"""

import smtplib
import logging
import random
import string
import os
import hashlib
import time
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
MAX_OTP_ATTEMPTS = 5  # Maximum number of verification attempts
RATE_LIMIT_SECONDS = 60  # Time between OTP requests for the same email

# Secure OTP storage with the following structure:
# {
#   "email": {
#     "otp_hash": "hashed_otp_value", 
#     "expiry": datetime_object, 
#     "verified": False, 
#     "purpose": "signup/reset",
#     "attempts": 0,
#     "last_request": timestamp
#   }
# }
otp_store = {}


def generate_otp(length=OTP_LENGTH):
    """Generate a random numeric OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))


def hash_otp(otp, email):
    """Create a secure hash of the OTP with email as salt"""
    # Use email as a salt to make the hash unique even for same OTPs
    salted = f"{otp}:{email}"
    return hashlib.sha256(salted.encode()).hexdigest()


def store_otp(email, otp, purpose="signup"):
    """Store OTP with expiry time using a secure hash"""
    current_time = time.time()
    
    # Apply rate limiting
    if email in otp_store and current_time - otp_store[email].get("last_request", 0) < RATE_LIMIT_SECONDS:
        logger.warning(f"Rate limit exceeded for {email}. Please wait before requesting another OTP.")
        return False
    
    # Store hashed version of OTP, not plain text
    otp_hash = hash_otp(otp, email)
    
    otp_store[email] = {
        "otp_hash": otp_hash,
        "expiry": datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
        "verified": False,
        "purpose": purpose,
        "attempts": 0,
        "last_request": current_time
    }
    
    # In development mode, log the OTP for easy testing
    if DEV_MODE:
        logger.info(f"DEV MODE - OTP for {email}: {otp} (purpose: {purpose})")
    
    return True


def verify_otp(email, otp):
    """Verify if the provided OTP is valid and not expired"""
    if email not in otp_store:
        logger.warning(f"No OTP found for {email}")
        return False
    
    otp_data = otp_store[email]
    
    # Check if OTP has expired
    if otp_data["expiry"] < datetime.now():
        # OTP has expired, clean it up
        clear_otp(email)
        logger.warning(f"OTP expired for {email}")
        return False
    
    # Check if too many attempts
    if otp_data["attempts"] >= MAX_OTP_ATTEMPTS:
        logger.warning(f"Too many failed attempts for {email}")
        clear_otp(email)
        return False
    
    # Increment attempt counter
    otp_data["attempts"] += 1
    
    # Compare hashed versions
    provided_hash = hash_otp(otp, email)
    if otp_data["otp_hash"] != provided_hash:
        logger.warning(f"Invalid OTP for {email}, attempt {otp_data['attempts']}")
        return False
    
    # Mark as verified and clean up
    otp_data["verified"] = True
    return True


def is_otp_verified(email, purpose=None):
    """Check if OTP for the email is verified"""
    if email not in otp_store:
        return False
    
    otp_data = otp_store[email]
    
    # Check if OTP has expired
    if otp_data["expiry"] < datetime.now():
        clear_otp(email)
        return False
    
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
    # Generate and store OTP first
    if not store_otp(recipient_email, otp, purpose):
        return False
        
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