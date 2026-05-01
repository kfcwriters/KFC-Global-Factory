import smtplib
import os
from email.message import EmailMessage

def send_outreach():
    if not os.path.exists('business_leads.txt'):
        print("❌ Error: business_leads.txt not found.")
        return

    with open('business_leads.txt', 'r') as f:
        lines = f.readlines()
    
    # Parsing the lead file
    try:
        target_email = lines[1].split(': ')[1].strip()
        # Subject is on Line 4, Body starts on Line 6
        subject = lines[4].split(': ')[1].strip()
        body = "".join(lines[6:])
    except Exception as e:
        print(f"❌ Parsing Error: {e}")
        return

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv('EMAIL_USER')
    msg['To'] = target_email

    try:
        # Standard SSL connection for Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
            smtp.send_message(msg)
        print(f"🚀 Outreach email successfully sent to: {target_email}")
    except Exception as e:
        print(f"❌ SMTP Error: {e}")

if __name__ == "__main__":
    send_outreach()
