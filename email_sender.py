import smtplib
import os
from email.message import EmailMessage

def send_outreach():
    if not os.path.exists('business_leads.txt'):
        print("❌ Lead file missing.")
        return

    target_email = ""
    subject = ""
    body = ""
    capture_body = False

    with open('business_leads.txt', 'r') as f:
        for line in f:
            if line.startswith("TARGET_EMAIL:"):
                target_email = line.split(": ")[1].strip()
            elif line.startswith("SUBJECT:"):
                subject = line.split(": ")[1].strip()
            elif line.startswith("BODY_START"):
                capture_body = True
                continue
            if capture_body:
                body += line

    if not target_email or not subject:
        print("❌ Could not parse lead data.")
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
