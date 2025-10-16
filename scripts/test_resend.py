import resend
import os
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

try:
    params = {
        "from": "onboarding@resend.dev",
        "to": ["wanfaliangusa@gmail.com"],  # PUT YOUR EMAIL HERE
        "subject": "Test Email",
        "html": "<p>This is a test!</p>",
    }
    
    response = resend.Emails.send(params)
    print(f"Success! Email ID: {response}")
except Exception as e:
    print(f"Error: {e}")