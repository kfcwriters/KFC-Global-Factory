import os
import requests
import random

def run_media_production():
    # 🔑 SECURE ACCESS: Pulling directly from your GitHub Secrets
    # This ensures your 'Credits' on the dashboard are actually used.
    SHOTSTACK_KEY = os.getenv('SHOTSTACK_KEY')
    tg_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337"

    if not SHOTSTACK_KEY:
        print("❌ ERROR: SHOTSTACK_KEY not found in Environment. Check GitHub Secrets.")
        return

    # 🔬 TOPIC ROTATION: Matching the PhD authority of your brand
    topics = [
        {"title": "Advanced Oncology Research 2026", "desc": "Next-gen biomarker tracking and precision therapy."},
        {"title": "Cardiovascular Clinical Updates", "desc": "New protocols in cardiology manuscript drafting."},
        {"title": "Biochemistry & Metabolic Signaling", "desc": "PhD-level analysis of cellular pathways."},
        {"title": "Surgical Narrative Excellence", "desc": "Transforming complex cases into Scopus-indexed papers."}
    ]
    strike = random.choice(topics)

    print(f"🎬 STUDIO: Initiating 1080p Render for {strike['title']}...")

    # 🎥 PRODUCTION ORDER: 720p HD + Direct YouTube Upload
    payload = {
        "timeline": {
            "background": "#000000",
            "tracks": [{
                "clips": [{
                    "asset": {
                        "type": "html",
                        "html": f"<div style='color:white; font-family:Arial; text-align:center;'><h1>{strike['title']}</h1><p>{strike['desc']}</p></div>",
                        "css": "div { margin-top: 450px; padding: 40px; background: rgba(0,0,0,0.8); border-radius: 20px; border: 2px solid #00d4ff; }"
                    },
                    "start": 0, "length": 10
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
                        "title": f"{strike['title']} | KFC Lab PhD Support",
                        "description": f"Expert medical writing for {strike['desc']}. Contact: kfcwriters@gmail.com",
                        "category": "27",
                        "privacy": "public"
                    }
                }
            ]
        }
    }

    headers = {
        "x-api-key": SHOTSTACK_KEY,
        "Content-Type": "application/json"
    }
    
    try
