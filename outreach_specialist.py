import os
import smtplib
from email.message import EmailMessage

def run_outreach():
    pwd = os.getenv('GMAIL_PASSWORD')
    if not os.path.exists("current_leads.txt") or not pwd:
        print("⚠️ No leads found or GMAIL_PASSWORD missing.")
        return

    with open("current_leads.txt", "r") as f:
        leads = [line.strip() for line in f.readlines()]

    print(f"📧 Launching Global Outreach to {len(leads)} clinicians...")
    
    for addr in leads:
        try:
            msg = EmailMessage()
            # Professional Broad-Spectrum Subject Line
            msg['Subject'] = "PhD Collaboration: Clinical Research Methodology & Manuscript Support"
            msg['From'] = "kfcwriters@gmail.com"
            msg['To'] = addr
            
            content = f"""Dear Colleague,

I am a Clinical Scientist and PhD Researcher specializing in Laboratory Quality Management and Meta-Analysis. I am reaching out to offer professional, PhD-level support for your upcoming medical manuscripts and clinical studies.

My expertise includes:
- Analytical Performance Optimization (Sigma Metrics)
- Systematic Reviews & Meta-Analysis
- Cross-checking clinical results with global literature

Whether you are in Surgery, Pathology, or Internal Medicine, I can ensure your research meets the highest analytical standards for high-impact publication.

Best Regards,

KFC Lab - Clinical Research Division
PhD Researcher | Clinical Scientist
"""
            msg.set_content(content)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("kfcwriters@gmail.com", pwd)
                smtp.send_message(msg)
            print(f"✅ Delivered: {addr}")
        except Exception as e:
            print(f"❌ Failed for {addr}: {e}")

if __name__ == "__main__":
    run_outreach()
