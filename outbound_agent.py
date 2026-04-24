import os
import requests
import smtplib
import random
import imaplib
import email
from email.message import EmailMessage

def execute_final_strike():
    # 🔑 Credentials
    tg_token = os.getenv('TELEGRAM_TOKEN')
    gmail_pass = os.getenv('GMAIL_PASSWORD')
    SHOTSTACK_KEY = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq" 
    my_email = "kfcwriters@gmail.com"
    chat_id = "1060905337"

    # 🔬 1. RESEARCH: Global Medical Field Rotation
    medical_vault = [
        {"field": "Oncology & Precision Medicine", "spec": "Novel biomarker analysis and immunotherapy clinical trials"},
        {"field": "Cardiovascular Sciences", "spec": "Protocol design and manuscript drafting for Cardiology trials"},
        {"field": "Advanced Surgical Techniques", "spec": "High-impact narrative drafting for complex surgical outcomes"},
        {"field": "Biochemistry & Metabolic Pathways", "spec": "PhD-level analysis of biomarkers and metabolic signaling"},
        {"field": "Pharmacovigilance & Drug Safety", "spec": "FDA/EMA Phase I-III protocol documentation and safety reporting"},
        {"field": "Pediatric Research & Clinical Trials", "spec": "Specialized manuscript support for pediatric clinical studies"}
    ]
    strike = random.choice(medical_vault)
    print(f"🚀 CEO: Initiating Global Strike on {strike['field']}")

    # 📧 2. OUTREACH: Elaborate Predator Pitch (Targeting Researchers)
    # We simulate a hunt for the top 5 global researchers in this field
    recipients = [f"lead.researcher{random.randint(1,99)}@medical-university.org", "careers@trilogywriting.com", "info@cactusglobal.com", "editorial@elsevier.com"]
    emails_sent = 0

    if gmail_pass:
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(my_email, gmail_pass)
                for recipient in recipients:
                    msg = EmailMessage()
                    msg['Subject'] = f"PhD-Level Medical Writing & Research Support: {strike['field']}"
                    msg['From'] = f"KFC Lab - Chief Research Specialist <{my_email}>"
                    msg['To'] = recipient
                    
                    body = (
                        "Dear Editorial Lead / Lead Researcher,\n\n"
                        "I am a Clinical Scientist and PhD Researcher providing end-to-end medical writing and publication support across the clinical spectrum.\n\n"
                        "Our team specializes in:\n"
                        "🧪 CLINICAL: Surgical Case Reports, Trials, and Meta-Analyses.\n"
                        "🎓 ACADEMIC: PhD Thesis drafting and MBBS Curriculum Design.\n"
                        "⚖️ REGULATORY: Pharma compliance and Biochemistry protocols.\n"
                        "📊 QUALITY: Six Sigma implementation in Laboratory Management.\n\n"
                        f"Currently, we are focusing on {strike['field']} with a specialty in {strike['spec']}.\n\n"
                        "I am available to assist your editorial team or doctoral candidates in producing high-impact, peer-reviewed content.\n\n"
                        "Best Regards,\n"
                        "KFC Lab - Chief Research Specialist"
                    )
                    msg.set_content(body)
                    server.send_message(msg)
                    emails_sent += 1
        except Exception as e: print(f"❌ Outreach Error: {e}")

    # 🎥 3. MEDIA: Make & Upload (Shotstack Destination)
    print(f"🎬 MEDIA: Making & Uploading 1080p Video for {strike['field']}...")
    media_status = "⚠️ Upload Failure"
    try:
        payload = {
            "timeline": {"tracks": [{"clips": [{"asset": {"type": "html", "html": f"<h1 style='color:white;'>{strike['field']}</h1>"}, "start": 0, "length": 10}]}]},
            "output": {
                "format": "mp4", "resolution": "hd1080",
                "destinations": [{"provider": "youtube", "options": {"title": f"{strike['field']} Research 2026", "category": "27", "privacy": "public"}}]
            }
        }
        headers = {"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"}
        resp = requests.post("https://api.shotstack.io/edit/v1/render", json=payload, headers=headers)
        if resp.status_code == 201: media_status = "✅ Render & Upload Started"
    except: pass

    # 📲 4. TELEGRAM: Commander Feedback Loop (Alerts on Replies)
    if tg_token:
        report = (
            f"✅ 24/7 FACTORY: FINAL STRIKE COMPLETE\n\n"
            f"🎯 FIELD: {strike['field']}\n"
            f"📧 OUTREACH: {emails_sent} Elaborate Pitches Sent.\n"
            f"🎥 VIDEO: {media_status}\n"
            "📊 STATUS: Total Medical Authority Active."
        )
        requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": chat_id, "text": report})

if __name__ == "__main__":
    execute_final_strike()
