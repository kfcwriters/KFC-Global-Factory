import os
import requests
import smtplib
import random
from email.message import EmailMessage

def execute_global_factory():
    # 🔑 Credentials
    tg_token = os.getenv('TELEGRAM_TOKEN')
    gmail_pass = os.getenv('GMAIL_PASSWORD')
    SHOTSTACK_KEY = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq" 
    my_email = "kfcwriters@gmail.com"
    chat_id = "1060905337"

    # 🔬 THE GLOBAL MEDICAL VAULT
    vault = [
        {"title": "ZBP1: mRNA Sentinel in Nephrology", "focus": "Diabetic Kidney Injury Tracking"},
        {"title": "Surgical Case Reports: Precision Narratives", "focus": "High-impact narrative drafting for surgeons"},
        {"title": "Regulatory Writing for Clinical Trials", "focus": "FDA/EMA Phase I-III Compliance"},
        {"title": "Myonectin & Metabolic Signaling", "focus": "CTRP15 and Lipid Metabolism in T2D"}
    ]
    strike = random.choice(vault)

    # 🎯 TARGET LIST WITH PERSONALIZATION TAGS
    # Format: (Email, Company/Name, Tone)
    targets = [
        ("freelancers@kwglobal.com", "KW Global Editorial Team", "Professional"),
        ("careers@trilogywriting.com", "Trilogy Writing Leads", "Academic"),
        ("info@cactusglobal.com", "Cactus Communications", "Innovative"),
        ("editorial@elsevier.com", "Elsevier Medical Journals", "Formal")
    ]

    emails_sent = 0
    if gmail_pass:
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(my_email, gmail_pass)
                
                for email, name, tone in targets:
                    msg = EmailMessage()
                    msg['Subject'] = f"PhD-Level Support for {name}: {strike['title']}"
                    msg['From'] = my_email
                    msg['To'] = email
                    
                    # 🛠️ THE DYNAMIC PERSONALIZATION ENGINE
                    greeting = f"Dear {name}," if tone != "Formal" else "To the Editorial Lead at Elsevier,"
                    
                    body = (
                        f"{greeting}\n\n"
                        f"As a Clinical Scientist and PhD Researcher, I have been following the high-standard publications coming out of {name}. "
                        "I am reaching out to provide specialized end-to-end medical writing support for your clinical spectrum.\n\n"
                        "Our Laboratory Specializes in:\n"
                        "🧪 CLINICAL: Surgical Case Reports, Meta-Analyses & Clinical Trials.\n"
                        "🎓 ACADEMIC: PhD Thesis drafting & MBBS/MLT Curriculum design.\n"
                        "⚖️ REGULATORY: Pharma compliance & Biochemistry protocols.\n"
                        "📊 QUALITY: Six Sigma & Laboratory Performance Management.\n\n"
                        f"We are currently finalizing research on {strike['title']}, with a specialty in {strike['focus']}.\n\n"
                        "I am available to assist your team or your associated doctoral candidates in producing high-impact, peer-reviewed content.\n\n"
                        "Best Regards,\n"
                        "KFC Lab - Chief Research Specialist\n"
                        "YouTube: @KFCwritersbot"
                    )
                    msg.set_content(body)
                    server.send_message(msg)
                    emails_sent += 1
            print(f"📧 Outreach: {emails_sent} personalized pitches dispatched.")
        except Exception as e: print(f"❌ Email Error: {e}")

    # 🎥 MEDIA AGENT (Shotstack 720P)
    media_status = "⚠️ Engine Failure"
    try:
        payload = {
            "timeline": {"tracks": [{"clips": [{"asset": {"type": "html", "html": f"<div style='color:#fff; font-family:Arial; text-align:center;'><h1>{strike['title']}</h1></div>", "css": "div { margin-top: 500px; }"}, "start": 0, "length": 10}]}]},
            "output": {"format": "mp4", "resolution": "hd720"}
        }
        headers = {"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"}
        requests.post("https://api.shotstack.io/edit/v1/render", json=payload, headers=headers)
        media_status = "✅ Render Active"
    except: media_status = "❌ Media Crash"

    # 📲 REPORT
    if tg_token:
        report = f"✅ 24/7 GLOBAL STRIKE: PERSONALIZED\n🎯 TOPIC: {strike['title']}\n📧 OUTREACH: {emails_sent} Custom Pitches Sent.\n🎥 MEDIA: {media_status}"
        requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": chat_id, "text": report})

if __name__ == "__main__":
    execute_global_factory()
