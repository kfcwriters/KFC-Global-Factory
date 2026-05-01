import smtplib
import os
from email.message import EmailMessage

def send_outreach():
    if not os.path.exists('business_leads.txt'):
        print("❌ Lead file not found.")
        return

    # Using GMAIL_USER and GMAIL_PASSWORD directly from environment
    user = os.getenv('GMAIL_USER')
    password = os.getenv('GMAIL_PASSWORD')

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
    msg['From'] = user
    msg['To'] = target_email

    try:
        # Standard Port 465 for Gmail App Passwords
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(user, password)
            server.send_message(msg)
        print(f"🚀 SUCCESS: Outreach sent to {target_email}")
    except smtplib.SMTPAuthenticationError:
        print("❌ 535 AUTH ERROR: Your App Password was rejected.")
        print("👉 FIX: Ensure you copied 'tnhyxpgbnkykelze' exactly into GMAIL_PASSWORD secret.")
    except Exception as e:
        print(f"❌ SMTP Error: {e}")

if __name__ == "__main__":
    send_outreach()
