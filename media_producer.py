import os
import requests
import random

def run_media_production():
    SHOTSTACK_KEY = os.getenv('SHOTSTACK_KEY')
    tg_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337"

    if not SHOTSTACK_KEY:
        print("❌ API Key Missing")
        return

    # 🔬 Topic Selection
    strike = {"title": "Clinical Research 2026", "desc": "PhD-level medical writing and support."}

    # 🎥 720p HD Production Order
    # Fixed the 'resolution' and 'destinations' structure to avoid 400 error
    payload = {
        "timeline": {
            "background": "#000000",
            "tracks": [{
                "clips": [{
                    "asset": {
                        "type": "html",
                        "html": f"<div style='color:white; text-align:center; font-family:Arial;'><h1>{strike['title']}</h1><p>{strike['desc']}</p></div>",
                        "css": "div { margin-top: 300px; }"
                    },
                    "start": 0, "length": 5
                }]
            }]
        },
        "output": {
            "format": "mp4",
            "resolution": "720", # Corrected resolution string
            "destinations": [
                {
                    "provider": "youtube",
                    "options": {
                        "title": f"{strike['title']} Update",
                        "description": strike['desc'],
                        "category": "27",
                        "privacy": "public"
                    }
                }
            ]
        }
    }

    headers = {"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"}
    
    try:
        response = requests.post("https://api.shotstack.io/edit/v1/render", json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            render_id = response.json().get('response', {}).get('id')
            print(f"✅ Render Started: {render_id}")
            if tg_token:
                requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": chat_id, "text": "🎬 Video Render Started!"})
        else:
            print(f"❌ Error Detail: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_media_production()
