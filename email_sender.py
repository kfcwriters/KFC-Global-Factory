import smtplib
import os
from email.message import EmailMessage

def send_outreach():
    if not os.path.exists('business_leads.txt'):
        print("❌ Lead file missing.")
        return

    with open('business_leads.txt', 'r') as f:
        lines = f.readlines()
    
    try:
        target_email = lines[1].split(': ')[1].strip()
        subject = lines[4].split(': ')[1].strip()
        body = "".join(lines[6:])
    except Exception as e:
        print(f"❌ Lead Format Error: {e}")
        return

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv('EMAIL_USER') # Code uses this for your Gmail address
    msg['To'] = target_email

    try:
        # Port 465 for SSL (Standard for Gmail App Passwords)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            # ALIGNMENT: Using GMAIL_PASSWORD from your Secrets
            server.login(os.getenv('EMAIL_USER'), os.getenv('GMAIL_PASSWORD'))
            server.send_message(msg)
        print(f"🚀 SUCCESS: Email sent to {target_email}")
    except Exception as e:
        print(f"❌ SMTP Error: {e}")
        print("💡 Ensure GMAIL_PASSWORD in GitHub is a 16-character App Password.")

if __name__ == "__main__":
    send_outreach()
