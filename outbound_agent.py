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

    # 🔬 THE GLOBAL MEDICAL VAULT (PhD Focus)
    vault = [
        {"title": "ZBP1: mRNA Sentinel in Nephrology", "focus": "Diabetic Kidney Injury Tracking"},
        {"title": "Surgical Case Reports: Precision Narratives", "focus": "High-impact narrative drafting for surgeons"},
        {"title": "Regulatory Writing for Clinical Trials", "focus": "FDA/EMA Phase I-III Compliance"},
        {"title": "Myonectin & Metabolic Signaling", "focus": "CTRP15 and Lipid Metabolism in T2D"},
        {"title": "Medical Education Curriculum Design", "focus": "MBBS & MLT automated assessment tools"}
    ]
    strike = random.choice(vault)
    print(f"🚀 CEO: Initiating Global Strike on {strike['title']}")

    # 📧 THE OUTREACH PREDATOR (Restored High-Authority Material)
    recipients = ["freelancers@kwglobal.com", "careers@trilogywriting.com", "info@cactusglobal.com", "editorial@elsevier.com"]
    emails_sent = 0

    if gmail_pass:
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(my_email, gmail_pass)
                for recipient in recipients:
                    msg = EmailMessage()
                    msg['Subject'] = f"PhD-Level Clinical Writing & Thesis Support: {strike['title']}"
                    msg['From'] = my_email
                    msg['To'] = recipient
                    
                    # 🎓 THE RESTORED POWER PITCH
                    body = (
                        "Dear Editorial Lead / Research Director,\n\n"
                        "I am a Clinical Scientist and PhD Researcher providing specialized medical writing and publication support across the clinical spectrum.\n\n"
                        "Our Services Include:\n"
                        "✅ CLINICAL: Surgical Case Reports, Trial Protocols, and Meta-Analyses.\n"
                        "✅ ACADEMIC: PhD Thesis drafting and MBBS/MLT Curriculum Design.\n"
                        "✅ REGULATORY: Pharma compliance and Biochemistry protocols.\n"
                        "✅ QUALITY: Six Sigma implementation in Laboratory Management.\n\n"
                        f"Current Field Highlight: {strike['title']}\n"
                        f"Specialization: {strike['focus']}\n\n"
                        "I am available to assist your editorial team or doctoral candidates in producing high-impact, peer-reviewed content that meets 2026 standards.\n\n"
                        "Best Regards,\n"
                        "KFC Lab - Chief Research Specialist\n"
                        "YouTube: @KFCwritersbot"
                    )
                    msg.set_content(body)
                    server.send_message(msg)
                    emails_sent += 1
            print(f"📧 Global Outreach: {emails_sent} specialized emails sent.")
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
                            "html": f"<div style='color:#fff; font-family:Arial; text-align:center;'><h1>{strike['title']}</h1><p>{strike['focus']}</p></div>",
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
            f"✅ 24/7 GLOBAL STRIKE COMPLETE\n\n"
            f"🎯 TOPIC: {strike['title']}\n"
            f"📧 OUTREACH: {emails_sent} Full-Authority Pitches Sent.\n"
            f"🎥 MEDIA AGENT: {media_status}\n"
            "📊 STATUS: Total Medical Authority Active."
        )
        requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": chat_id, "text": report})

if __name__ == "__main__":
    execute_global_factory()
