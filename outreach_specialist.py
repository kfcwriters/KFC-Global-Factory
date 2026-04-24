import os
import smtplib
import time
from email.message import EmailMessage

def send_outreach(email_list):
    # 🛡️ THE IRON BARRIER
    forbidden = ["info", "admin", "office", "support", "contact", "sales", "help"]
    
    for addr in email_list:
        clean_addr = addr.lower().strip()
        if any(word in clean_addr for word in forbidden):
            continue
            
        try:
            msg = EmailMessage()
            msg['Subject'] = "PhD-Level Collaboration: Medical Manuscript & Sigma Metrics Support"
            msg['From'] = "kfcwriters@gmail.com"
            msg['To'] = clean_addr
            
            # High-Authority Professional Body
            body = f"""Dear Researcher,

I am a Clinical Scientist and PhD Researcher specializing in Clinical Biochemistry and Analytical Quality Management. 

I am reaching out to offer specialized support for your upcoming medical manuscripts. Our division provides expert assistance in:

✅ Systematic Reviews & Meta-Analysis (e.g., Myonectin and T2DM complications)
✅ Sigma Metrics & Risk-Based Quality Management for Clinical Labs
✅ High-Impact Journal Submission (Scopus, PubMed, ScienceDirect)
✅ Professional Clinical Narrative Drafting

We ensure your research meets the highest international standards for rapid peer-review acceptance.

Best Regards,
KFC Lab - Clinical Research Division
Lead PhD Consultant"""

            msg.set_content(body)
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("kfcwriters@gmail.com", os.getenv('GMAIL_PASSWORD'))
                smtp.send_message(msg)
            print(f"✅ DELIVERED: PhD Pitch sent to {clean_addr}")
            
            # Anti-Spam Pause
            time.sleep(2) 
            
        except Exception as e:
            print(f"⚠️ Mailbox Error for {clean_addr}: {e}")
            continue
