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
            msg['Subject'] = "PhD Collaboration: Analytical Quality & Sigma Metrics"
            msg['From'] = "kfcwriters@gmail.com"
            msg['To'] = addr
            msg.set_content(f"Dear Dr. Researcher,\n\nI offer PhD-level support in Clinical Biochemistry and Sigma Metrics for your manuscripts indexed in DOAJ/Copernicus.\n\nBest,\nKFC Lab")

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("kfcwriters@gmail.com", pwd)
                smtp.send_message(msg)
            print(f"✅ Pitch Delivered: {addr}")
        except Exception as e:
            print(f"❌ Outreach Error {addr}: {e}")

if __name__ == "__main__":
    run_outreach()
