import os
import requests

def run_media_production():
    SHOTSTACK_KEY = os.getenv('SHOTSTACK_KEY')
    tg_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337"

    if not SHOTSTACK_KEY:
        print("❌ API Key Missing")
        return

    # 🔬 Hardcoded topic for the first successful render
    title = "Clinical Biochemistry Update 2026"

    # 🎥 THE HARDENED PAYLOAD
    # I have removed complex CSS and nested HTML to ensure zero errors.
    payload = {
        "timeline": {
            "tracks": [
                {
                    "clips": [
                        {
                            "asset": {
                                "type": "title",
                                "text": title,
                                "style": "future"
                            },
                            "start": 0,
                            "length": 5
                        }
                    ]
                }
            ]
        },
        "output": {
            "format": "mp4",
            "resolution": "720"
        }
    }

    # 🔥 IMPORTANT: Adding destinations OUTSIDE the render call if needed, 
    # but for the first success, let's just get the video made.
    
    headers = {
        "x-api-key": SHOTSTACK_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        # Using the standard edit endpoint
        response = requests.post("https://api.shotstack.io/edit/v1/render", json=payload, headers=headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            render_id = response.json().get('response', {}).get('id')
            print(f"✅ SUCCESS! Render ID: {render_id}")
            if tg_token:
                requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": chat_id, "text": f"🎬 SUCCESS! Video rendering: {render_id}"})
        else:
            print(f"❌ REJECTED: {response.text}")
            
    except Exception as e:
        print(f"❌ CRASH: {e}")

if __name__ == "__main__":
    run_media_production()
