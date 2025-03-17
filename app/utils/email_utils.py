# app/utils/email_utils.py

import smtplib
import os
from email.mime.text import MIMEText

def send_email(to_email, subject, message):
    """Send an email notification using Gmail SMTP."""

    # Your Gmail account details
    sender_email = "aminisouissi@gmail.com"
    sender_password = os.getenv("EMAIL_PASSWORD")  # Securely stored in environment variables

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:  # Gmail SMTP server
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")
