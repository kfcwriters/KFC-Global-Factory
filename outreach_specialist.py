import os
import smtplib
from email.message import EmailMessage

def send_outreach(email_list):
    # 🛡️ THE IRON GATE: Blocking generic roles
    trash = ["info", "admin", "office", "support", "contact", "sales"]
    
    # 📝 THE PROFESSIONAL PhD PITCH
    subject = "PhD-Level Support: Specialized Medical Manuscript & Publication Assistance"
    
    for addr in email_list:
        clean_addr = addr.lower().strip()
        if any(word in clean_addr for word in trash):
            continue
            
        try:
            msg = EmailMessage()
            # Detailed, High-Authority Body
            body = f"""Dear Lead Researcher,

I am a Clinical Scientist and PhD Researcher specializing in clinical biochemistry and laboratory quality management. I am reaching out to offer specialized, high-level support for your upcoming medical manuscripts and research publications.

Our Laboratory Excellence team provides expert assistance in:
✅ Statistical Analysis & Sigma Metrics (Analytical Quality Management)
✅ Systematic Reviews & Meta-Analysis (e.g., Myonectin/T2DM studies)
✅ Clinical Narrative Drafting & Case Report Publication
✅ Regulatory Compliance for Scopus, PubMed, and ScienceDirect

We help researchers maintain the highest international standards of clinical documentation to ensure rapid acceptance in high-impact journals.

Best Regards,
Chief Research Specialist
KFC Lab - Clinical Research Division"""

            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = "kfcwriters@gmail.com"
            msg['To'] = clean_addr
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("kfcwriters@gmail.com", os.getenv('GMAIL_PASSWORD'))
                smtp.send_message(msg)
            print(f"✅ Successfully delivered PhD pitch to: {clean_addr}")
            
        except Exception as e:
            print(f"⚠️ Skipping {clean_addr} due to technical error: {e}")
            continue
