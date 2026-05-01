import smtplib
import os
from email.message import EmailMessage

def send_outreach():
    if not os.path.exists('business_leads.txt'):
        print("❌ Lead file not found.")
        return

    with open('business_leads.txt', 'r') as f:
        lines = f.readlines()
    
    try:
        # Parsing: EMAIL is on Line 2, Subject is on Line 4
        target_email = lines[1].split(': ')[1].strip()
        subject = lines[4].split(': ')[1].strip()
        body = "".join(lines[6:])
    except Exception as e:
        print(f"❌ Formatting Error: {e}")
        return

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv('EMAIL_USER')
    msg['To'] = target_email

    try:
        # Standard SSL Port 465 for Gmail App Passwords
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            # Using your exact secret name
            server.login(os.getenv('EMAIL_USER'), os.getenv('GMAIL_PASSWORD'))
            server.send_message(msg)
        print(f"🚀 SUCCESS: Outreach sent to {target_email}")
    except Exception as e:
        print(f"❌ SMTP Error: {e}")

if __name__ == "__main__":
    send_outreach()
