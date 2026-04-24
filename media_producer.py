import os
import requests
import random

def run_media_production():
    # 🔑 Credentials from GitHub Secrets
    SHOTSTACK_KEY = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq"
    tg_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337"

    # 🔬 Select a Trending Clinical Field for the Video
    # We match this to the topics the Hunter is using
    fields = [
        {"title": "Advanced Oncology Research 2026", "desc": "Next-gen biomarker tracking and precision therapy."},
        {"title": "Cardiovascular Clinical Updates", "desc": "New protocols in cardiology manuscript drafting."},
        {"title": "Biochemistry & Metabolic Signaling", "desc": "PhD-level analysis of cellular pathways."},
        {"title": "Surgical Narrative Excellence", "desc": "Transforming complex cases into Scopus-indexed papers."}
    ]
    strike = random.choice(fields)

    print(f"🎬 STUDIO: Making 1080p Video for {strike['title']}...")

    # 🎥 The Work Order for the Media Agent (1080p + Auto-Upload)
    payload = {
        "timeline": {
            "tracks": [{
                "clips": [{
                    "asset": {
                        "type": "html",
                        "html": f"<div style='color:white; font-family:Arial; text-align:center;'><h1>{strike['title']}</h1><p>{strike['desc']}</p></div>",
                        "css": "div { margin-top: 450px; padding: 40px; background: rgba(0,0,0,0.7); border-radius: 15px; }"
                    },
                    "start": 0, "length": 15
                }]
            }]
        },
        "output": {
            "format": "mp4",
            "resolution": "hd1080",
            "destinations": [
                {
                    "provider": "youtube",
                    "options": {
                        "title": f"{strike['title']} - PhD Research Support",
                        "description": f"Specialized medical writing and publication support for {strike['desc']}. Contact kfcwriters@gmail.com",
                        "category": "27", # Education
                        "privacy": "public"
                    }
                }
            ]
        }
    }

    headers = {"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"}
    
    try:
        response = requests.post("https://api.shotstack.io/edit/v1/render", json=payload, headers=headers)
        
        if response.status_code == 201:
            render_id = response.json().get('response', {}).get('id', 'N/A')
            status_msg = f"✅ VIDEO SUCCESS: 1080p Render & Upload Started.\nID: {render_id}"
        else:
            status_msg = f"❌ VIDEO ERROR: Shotstack returned {response.status_code}"
            
    except Exception as e:
        status_msg = f"❌ VIDEO CRASH: {e}"

    # 📲 Report to Telegram
    if tg_token:
        requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": chat_id, "text": status_msg})

if __name__ == "__main__":
    run_media_production()
