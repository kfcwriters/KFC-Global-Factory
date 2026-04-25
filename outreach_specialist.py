import os
import smtplib
from email.message import EmailMessage

def run_outreach():
    pwd = os.getenv('GMAIL_PASSWORD')
    if not os.path.exists("current_leads.txt") or not pwd:
        print("⚠️ No leads found or missing GMAIL_PASSWORD.")
        return

    with open("current_leads.txt", "r") as f:
        leads = [line.strip() for line in f.readlines()]

    print(f"📧 Launching outreach to {len(leads)} researchers...")
    
    for addr in leads:
        try:
            msg = EmailMessage()
            msg['Subject'] = "PhD Collaboration: Clinical Biochemistry & Sigma Metrics"
            msg['From'] = "kfcwriters@gmail.com"
            msg['To'] = addr
            msg.set_content(f"Dear Dr. Researcher,\n\nI provide PhD-level support for manuscripts and Laboratory Quality Management. Let's optimize your analytical quality together.\n\nBest,\nKFC Lab")

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("kfcwriters@gmail.com", pwd)
                smtp.send_message(msg)
            print(f"✅ Delivered: {addr}")
        except Exception as e:
            print(f"❌ Error {addr}: {e}")

if __name__ == "__main__":
    run_outreach()
