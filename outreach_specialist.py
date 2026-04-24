import os
import smtplib
from email.message import EmailMessage

def send_outreach(email_list):
    if not email_list:
        print("❌ Outreach Aborted: No valid authors found this hour.")
        return

    # 📝 THE PROFESSIONAL PhD PITCH
    subject = "PhD-Level Support: Specialized Medical Manuscript & Publication Assistance"
    
    for addr in email_list:
        try:
            msg = EmailMessage()
            body = f"""Dear Dr. Researcher,

I am a Clinical Scientist and PhD Researcher specializing in clinical biochemistry and laboratory quality management. 

I am reaching out to offer specialized support for your medical research publications. Our team provides expert assistance in:
✅ Systematic Reviews & Meta-Analysis (e.g., Myonectin and Diabetic Complications)
✅ Sigma Metrics & Analytical Quality Management for Labs
✅ Manuscript Drafting & Scopus/PubMed Submission
✅ Case Report Narrative Professionalism

We help researchers maintain the highest international standards of clinical documentation for rapid journal acceptance.

Best Regards,
KFC Lab - Clinical Research Division
Chief PhD Consultant"""

            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = "kfcwriters@gmail.com"
            msg['To'] = addr
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("kfcwriters@gmail.com", os.getenv('GMAIL_PASSWORD'))
                smtp.send_message(msg)
            print(f"✅ DELIVERED: Original Author Pitch sent to {addr}")
            
        except Exception as e:
            print(f"⚠️ Delivery failure for {addr}: {e}")
