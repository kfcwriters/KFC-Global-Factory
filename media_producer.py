import os
import requests

def run_media_production():
    key = os.getenv('SHOTSTACK_KEY')
    tg_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337"

    if not key:
        print("❌ ERROR: Key is empty.")
        return

    # 🔬 Bulletproof Payload
    payload = {
        "timeline": {
            "tracks": [{"clips": [{"asset": {"type": "title", "text": "KFC LAB"}, "start": 0, "length": 2}]}]
        },
        "output": {"format": "mp4", "resolution": "sd"}
    }

    # 🌐 We will try PRODUCTION first, then STAGING if it fails.
    endpoints = [
        "https://api.shotstack.io/edit/v1/render",
        "https://api.shotstack.io/v1/render"
    ]

    for url in endpoints:
        try:
            print(f"📡 Attempting: {url}")
            response = requests.post(url, json=payload, headers={"x-api-key": key, "Content-Type": "application/json"})
            
            if response.status_code == 201:
                render_id = response.json().get('response', {}).get('id')
                print(f"✅ SUCCESS on {url}! ID: {render_id}")
                if tg_token:
                    requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": chat_id, "text": f"🎬 VIDEO LIVE: {render_id}"})
                return # Exit once successful
            else:
                print(f"❌ Rejected by {url}: {response.text}")
        except Exception as e:
            print(f"⚠️ Connection error on {url}: {e}")

if __name__ == "__main__":
    run_media_production()
