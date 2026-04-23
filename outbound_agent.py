import os
import requests
import smtplib
import random
from email.message import EmailMessage

def execute_global_factory():
    # 🔑 Credentials & System Access
    tg_token = os.getenv('TELEGRAM_TOKEN')
    gmail_pass = os.getenv('GMAIL_PASSWORD')
    # 🎥 Media Agent: Shotstack Production Key
    SHOTSTACK_KEY = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq" 
    
    my_email = "kfcwriters@gmail.com"
    chat_id = "1060905337"

    # 🔬 THE GLOBAL MEDICAL VAULT (Dynamic Rotation for Variety)
    vault = [
        {"field": "Cardiovascular Clinical Trials", "spec": "Protocol design and manuscript drafting for high-impact Cardiology trials"},
        {"field": "Biochemistry & Metabolic Pathways", "spec": "PhD-level analysis of biomarkers, mitochondrial protection, and metabolic signaling"},
        {"field": "Surgical Case Reports & Narratives", "spec": "Converting complex surgical outcomes into peer-reviewed narratives for Scopus-indexed journals"},
        {"field": "Regulatory Pharma Compliance", "spec": "FDA/EMA Phase I-III protocol documentation and medical monitoring summaries"},
        {"field": "Medical Education & Curriculum", "spec": "Development of MBBS and MLT curriculum materials and automated assessment tools"}
    ]
    strike = random.choice(vault)
    print(f"🚀 CEO: Initiating Global Strike on {strike['field']}")

    # 📧 THE OUTREACH PREDATOR (Elaborated for High Conversion)
    recipients = ["freelancers@kwglobal.com", "careers@trilogywriting.com", "info@cactusglobal.com", "editorial@elsevier.com"]
    emails_sent = 0

    if gmail_pass:
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(my_email, gmail_pass)
                for recipient in recipients:
                    msg = EmailMessage()
                    msg['Subject'] = f"PhD-Level Medical Writing & Research Support: {strike['field']}"
                    msg['From'] = f"KFC Lab - Research Specialist <{my_email}>"
                    msg['To'] = recipient
                    
                    # 🎓 ELABORATED PROFESSIONAL MESSAGE
                    body = (
                        "Dear Editorial Lead,\n\n"
                        "I am a Clinical Scientist and PhD Researcher providing end-to-end medical writing and publication support across the entire clinical spectrum. "
                        "Our goal is to ensure your manuscripts and research projects meet the highest peer-reviewed standards for 2026.\n\n"
                        "Our team specializes in:\n"
                        "🧪 CLINICAL: Specialized Surgical Case Reports, Meta-Analyses, and Systematic Reviews.\n"
                        "🎓 ACADEMIC: PhD Thesis drafting, Grant writing, and MBBS/MLT Curriculum Design.\n"
                        "⚖️ REGULATORY: Pharma compliance (FDA/EMA), Biochemistry protocols, and Drug Safety reporting.\n"
                        "📊 QUALITY: Six Sigma implementation and Statistical Performance in Laboratory Management.\n\n"
                        f"Currently, our focus is on {strike['field']} with a specialized focus on {strike['spec']}.\n\n"
                        "We assist editorial teams, CROs, and doctoral candidates in accelerating the journey from raw data to high-impact publication. "
                        "I am available to discuss how we can support your upcoming projects or assist your associated researchers.\n\n"
                        "Best Regards,\n\n"
                        "KFC Lab - Chief Research Specialist\n"
                        "Web: PhD Clinical Research Division\n"
                        "YouTube: @KFCwritersbot"
                    )
                    msg.set_content(body)
                    server.send_message(msg)
                    emails_sent += 1
            print(f"📧 Global Outreach: {emails_sent} elaborated emails sent.")
        except Exception as e: print(f"❌ Email Error: {e}")

    # 🎥 MEDIA AGENT (Shotstack 720P Render)
    media_status = "⚠️ Engine Failure"
    try:
        payload = {
            "timeline": {
                "tracks": [{
                    "clips": [{
                        "asset": {
                            "type": "html",
                            "html": f"<div style='color:#fff; font-family:Arial; text-align:center;'><h1>{strike['field']}</h1><p>{strike['spec']}</p></div>",
                            "css": "div { margin-top: 400px; padding: 40px; background: rgba(0,0,0,0.6); border-radius: 20px; }"
                        },
                        "start": 0, "length": 15
                    }]
                }]
            },
            "output": {"format": "mp4", "resolution": "hd720"}
        }
        headers = {"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"}
        response = requests.post("https://api.shotstack.io/edit/v1/render", json=payload, headers=headers)
        media_status = f"✅ Render Started (ID: {response.json().get('response', {}).get('id', 'N/A')})" if response.status_code == 201 else f"❌ API Error: {response.status_code}"
    except Exception as e: media_status = f"❌ Media Crash: {e}"

    # 📲 COMMANDER REPORT
    if tg_token:
        report = (
            f"✅ 24/7 GLOBAL STRIKE: FULLY ELABORATED\n\n"
            f"🎯 TOPIC: {strike['field']}\n"
            f"📧 OUTREACH: {emails_sent} High-Conversion Pitches Sent.\n"
            f"🎥 MEDIA AGENT: {media_status}\n"
            "📊 STATUS: PhD Authority Active."
        )
        requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": chat_id, "text": report})

if __name__ == "__main__":
    execute_global_factory()
