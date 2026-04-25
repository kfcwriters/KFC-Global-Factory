import os
import smtplib
from email.message import EmailMessage

def run_outreach():
    pwd = os.getenv('GMAIL_PASSWORD')
    if not os.path.exists("current_leads.txt") or not pwd:
        return

    with open("current_leads.txt", "r") as f:
        leads = [line.strip() for line in f.readlines()]

    print(f"📧 Launching Professional Outreach to {len(leads)} Medical Scientists...")
    
    for addr in leads:
        try:
            msg = EmailMessage()
            msg['Subject'] = "Inquiry: PhD-Level Support for Advanced Medical Research & Sigma Quality"
            msg['From'] = "kfcwriters@gmail.com"
            msg['To'] = addr
            
            # Institutional PhD Pitch
            content = f"""Dear Esteemed Researcher,

I am a Clinical Scientist and PhD Researcher specializing in Clinical Biochemistry and Laboratory Quality Management. Having monitored your recent contributions to the medical science community, I am reaching out to offer professional, PhD-level support for your upcoming publications.

My expertise includes:
• Analytical Performance Optimization (Sigma Metrics & FMEA)
• Clinical Research Data Interpretation & Statistical Analysis
• Systematic Reviews and Meta-Analyses for Chronic Pathologies
• Laboratory Automation and Risk-Based Quality Management

Whether you require a second set of expert eyes on your methodology or assistance in aligning your findings with current global clinical literature, I am here to ensure your work achieves the highest analytical standard.

I look forward to discussing a potential collaboration on your next manuscript.

Best Regards,

KFC Lab - Clinical Research Division
PhD Researcher | Clinical Scientist
"""
            msg.set_content(content)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("kfcwriters@gmail.com", pwd)
                smtp.send_message(msg)
            print(f"✅ Formal Pitch Delivered: {addr}")
        except Exception as e:
            print(f"❌ Delivery Error {addr}: {e}")

if __name__ == "__main__":
    run_outreach()
