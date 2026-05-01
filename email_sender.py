import smtplib
import os
from email.message import EmailMessage

def send_outreach():
    if not os.path.exists('business_leads.txt'):
        return

    with open('business_leads.txt', 'r') as f:
        lines = f.readlines()
    
    try:
        # SANITIZE: Remove double dots and extra spaces automatically
        target_email = lines[1].split(': ')[1].strip().replace('..', '.')
        subject = lines[4].split(': ')[1].strip()
        body = "".join(lines[6:])
    except Exception as e:
        print(f"❌ Lead Format Error: {e}")
        return

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv('GMAIL_USER')
    msg['To'] = target_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_PASSWORD'))
            server.send_message(msg)
        print(f"🚀 SUCCESS: Email sent to {target_email}")
    except Exception as e:
        print(f"❌ SMTP Error: {e}")

if __name__ == "__main__":
    send_outreach()
