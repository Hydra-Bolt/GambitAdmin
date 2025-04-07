import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_smtp():
    # Email credentials
    sender_email = "ahmed4507537@gmail.com"
    app_password = "knab envl wghr phdg"  # App password, not regular password
    recipient_email = "amubashir200018@gmail.com"  # Send to yourself for testing
    
    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "SMTP Test Email"
    
    # Email body
    body = "This is a test email to verify SMTP connection with Gmail is working correctly."
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        
        # Login to account
        server.login(sender_email, app_password)
        
        # Send email
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)
        
        # Terminate session
        server.quit()
        print("Test email sent successfully!")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_gmail_smtp()