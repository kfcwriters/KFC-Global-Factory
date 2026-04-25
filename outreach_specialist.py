import os
import smtplib
from email.message import EmailMessage

def send_outreach():
    if not os.path.exists("current_leads.txt"):
        print("❌ No leads file found.")
        return

    with open("current_leads.txt", "r") as f:
        email_list = [line.strip() for line in f.readlines()]

    print(f"📧 Outreach Agent starting for {len(email_list)} authors...")

    for addr in email_list:
        try:
            msg = EmailMessage()
            msg['Subject'] = "PhD-Level Support: Medical Manuscript & Sigma Metrics Assistance"
            msg['From'] = "kfcwriters@gmail.com"
            msg['To'] = addr
            
            body = f"""Dear Dr. Researcher,

I am a Clinical Scientist specializing in Clinical Biochemistry and Sigma Metrics. 

I am offering PhD-level support for your upcoming medical manuscripts, including Meta-Analysis, systematic reviews, and high-impact journal submissions.

Best Regards,
KFC Lab - Clinical Research Division"""

            msg.set_content(body)
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("kfcwriters@gmail.com", os.getenv('GMAIL_PASSWORD'))
                smtp.send_message(msg)
            print(f"✅ DELIVERED: {addr}")
        except Exception as e:
            print(f"⚠️ Error sending to {addr}: {e}")

if __name__ == "__main__":
    send_outreach()
