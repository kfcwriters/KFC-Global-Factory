import smtplib
import os
import time
from email.message import EmailMessage

def send_5_outreach_emails():
    if not os.path.exists('business_leads.txt'):
        return

    content = open('business_leads.txt', 'r').read()
    leads = content.split('---LEAD_')
    
    # SMTP Login (Done once for efficiency)
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_PASSWORD'))
    except Exception as e:
        print(f"❌ Login Error: {e}")
        return

    for block in leads[1:]: # Skip the first empty split
        try:
            target_email = ""
            subject = ""
            body = ""
            capture_body = False
            
            lines = block.split('\n')
            for line in lines:
                if line.startswith("TARGET_EMAIL:"):
                    target_email = line.split(": ")[1].strip()
                elif line.startswith("SUBJECT:"):
                    subject = line.split(": ")[1].strip()
                elif "BODY_START" in line:
                    capture_body = True
                    continue
                elif "---END---" in line:
                    capture_body = False
                    continue
                if capture_body:
                    body += line + "\n"

            if target_email:
                msg = EmailMessage()
                msg.set_content(body)
                msg['Subject'] = subject
                msg['From'] = os.getenv('GMAIL_USER')
                msg['To'] = target_email
                
                server.send_message(msg)
                print(f"🚀 SUCCESS: Email sent to {target_email}")
                time.sleep(2) # Prevent spam flagging
        except Exception as e:
            print(f"⚠️ Failed to send a lead: {e}")

    server.quit()

if __name__ == "__main__":
    send_5_outreach_emails()
