import os
import requests
import smtplib
import random
from email.message import EmailMessage

def execute_global_factory():
    # 🔑 Credentials & System Access
    tg_token = os.getenv('TELEGRAM_TOKEN')
    gmail_pass = os.getenv('GMAIL_PASSWORD')
    # 🎥 Media Agent Hired: Shotstack Production Key
    SHOTSTACK_KEY = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq" 
    
    my_email = "kfcwriters@gmail.com"
    chat_id = "1060905337"

    # 🔬 DEPARTMENT 1: Research & Global Medical Vault
    # Multi-field coverage: Surgery, Pharma, Biochemistry, Education
    vault = [
        {"title": "ZBP1: mRNA Sentinel in Nephrology", "focus": "Diabetic Kidney Injury Tracking", "yt_tags": "Nephrology, PhD, Biomarkers"},
        {"title": "Surgical Case Reports: Precision Narratives", "focus": "High-impact narrative drafting for surgeons", "yt_tags": "Surgery, MedicalWriting, CaseReport"},
        {"title": "Regulatory Writing for Clinical Trials", "focus": "FDA/EMA Phase I-III Compliance", "yt_tags": "ClinicalTrials, Pharma, FDA"},
        {"title": "Myonectin & Metabolic Signaling", "focus": "CTRP15 and Lipid Metabolism in T2D", "yt_tags": "Biochemistry, PhD, Diabetes"},
        {"title": "Medical Education Curriculum Design", "focus": "MBBS & MLT automated assessment tools", "yt_tags": "MedicalEducation, MBBS, Education"}
    ]
    strike = random.choice(vault)
    print(f"🚀 CEO: Initiating Global Strike on {strike['title']}")

    # 🔭 DEPARTMENT 2: The Lead Hunter (Search Interception)
    leads = ["freelancers@kwglobal.com", "careers@trilogywriting.com", "info@cactusglobal.com", "editorial@elsevier.com"]
    emails_sent = 0

    # 📧 DEPARTMENT 3: The Outreach Predator (Gmail)
    if gmail_pass:
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(my_email, gmail_pass)
                for recipient in leads:
                    msg = EmailMessage()
                    msg['Subject'] = f"PhD-Level Clinical Writing Support: {strike['title']}"
                    msg['From'] = my_email
                    msg['To'] = recipient
                    
                    body = (
                        f"Dear Lead,\n\nI am a PhD Clinical Scientist providing specialized support for {strike['title']}.\n"
                        f"Field Focus: {strike['focus']}\n\n"
                        "I assist surgeons, researchers, and candidates in transforming clinical data into high-impact publications.\n\n"
                        "Best Regards,\nKFC Lab - Chief Research Specialist"
                    )
                    msg.set_content(body)
                    server.send_message(msg)
                    emails_sent += 1
            print(f"📧 Outreach: {emails_sent} specialized emails sent.")
        except Exception as e: print(f"❌ Outreach Error: {e}")

    # 🎥 DEPARTMENT 4: The Media Agent (Shotstack Cloud Rendering)
    media_status = "⚠️ Media Engine Failure"
    try:
        print(f"🎬 MEDIA AGENT: Ordering 720P Vertical Video for {strike['title']}...")
        
        # 720P Vertical (9:16) for YouTube Shorts
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
        
        if response.status_code == 201:
            render_id = response.json().get('response', {}).get('id', 'N/A')
            media_status = f"✅ 720P Render Started (ID: {render_id})"
        else:
            media_status = f"❌ API Error: {response.status_code}"
    except Exception as e: media_status = f"❌ Media Crash: {e}"

    # 📲 DEPARTMENT 5: Commander Reporting (Telegram)
    if tg_token:
        report = (
            f"✅ 24/7 GLOBAL FACTORY: FULL STRIKE\n\n"
            f"🎯 TOPIC: {strike['title']}\n"
            f"🔬 FOCUS: {strike['focus']}\n"
            f"📧 OUTREACH: {emails_sent} Global Pitches Sent.\n"
            f"🎥 MEDIA AGENT: {media_status}\n"
            "📊 STATUS: PhD Authority Active."
        )
        requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": chat_id, "text": report})
        print("📲 Telegram: Report delivered.")

if __name__ == "__main__":
    execute_global_factory()
