import resend
from datetime import datetime, timedelta
import secrets
from ..config import settings

# Initialize Resend
resend.api_key = settings.RESEND_API_KEY

def generate_verification_token() -> tuple[str, datetime]:
    """Generate a secure verification token and expiration time"""
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=24)  # Token valid for 24 hours
    return token, expires

def send_verification_email(email: str, token: str, user_name: str = None):
    """Send verification email using Resend"""
    
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    resend.api_key = settings.RESEND_API_KEY
        
    greeting = f"Hi {user_name}," if user_name else "Hi,"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Verify Your Email Address</h2>
            <p>{greeting}</p>
            <p>Thank you for registering with our Financial Analysis Platform!</p>
            <p>Please verify your email address by clicking the button below:</p>
            <a href="{verification_url}" class="button">Verify Email Address</a>
            <p>Or copy and paste this link into your browser:</p>
            <p style="color: #667eea; word-break: break-all;">{verification_url}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account, you can safely ignore this email.</p>
            <div class="footer">
                <p>Best regards,<br>Financial Analysis Platform Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        params = {
            "from": settings.FROM_EMAIL,
            "to": [email],
            "subject": "Verify Your Email Address",
            "html": html_content,
        }
        
        response = resend.Emails.send(params)
        print(f"✓ Verification email sent to {email}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to send email: {e}")
        return False


def send_welcome_email(email: str, user_name: str = None):
    """Send welcome email after verification"""
    
    greeting = f"Hi {user_name}," if user_name else "Hi,"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Welcome to Financial Analysis Platform! 🎉</h2>
            <p>{greeting}</p>
            <p>Your email has been successfully verified!</p>
            <p>You can now access all features of our platform:</p>
            <ul>
                <li>Create comprehensive financial analyses</li>
                <li>Generate detailed equity reports</li>
                <li>Track multiple companies</li>
                <li>Export data to Excel</li>
            </ul>
            <a href="{settings.FRONTEND_URL}/dashboard" class="button">Go to Dashboard</a>
            <p>If you have any questions, feel free to reach out to our support team.</p>
            <p>Happy analyzing!</p>
        </div>
    </body>
    </html>
    """
    
    try:
        params = {
            "from": settings.FROM_EMAIL,
            "to": [email],
            "subject": "Welcome to Financial Analysis Platform!",
            "html": html_content,
        }
        
        resend.Emails.send(params)
        print(f"✓ Welcome email sent to {email}")
        
    except Exception as e:
        print(f"✗ Failed to send welcome email: {e}")