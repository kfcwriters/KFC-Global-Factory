import os
import smtplib
from email.message import EmailMessage

def send_outreach(email_list):
    # 🛡️ THE PhD SHIELD (Same filter as before)
    trash = ["info", "admin", "office", "support", "contact", "sales"]
    
    # 📧 SETUP GMAIL
    msg_content = "Dear Lead Researcher, I am a Clinical Scientist providing specialized PhD-level support for medical manuscript writing and publication..."
    
    # NEW: Safety loop to prevent Gmail 550 errors from stopping the factory
    for addr in email_list:
        clean_addr = addr.lower().strip()
        if any(word in clean_addr for word in trash):
            continue
            
        try:
            # Create the email
            msg = EmailMessage()
            msg.set_content(msg_content)
            msg['Subject'] = "PhD-Level Support for Medical Sciences Publication"
            msg['From'] = "kfcwriters@gmail.com"
            msg['To'] = clean_addr
            
            # Send (Using your secrets)
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("kfcwriters@gmail.com", os.getenv('GMAIL_PASSWORD'))
                smtp.send_message(msg)
            print(f"✅ Successfully sent to: {clean_addr}")
            
        except Exception as e:
            print(f"⚠️ Skipping {clean_addr} due to server error: {e}")
            continue # This is the key—it keeps the factory running!
