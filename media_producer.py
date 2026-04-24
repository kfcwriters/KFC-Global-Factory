import os
import requests

def run_media_production():
    # 🔑 Pulling from GitHub Secrets
    key = os.getenv('SHOTSTACK_KEY')
    tg_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337"

    if not key:
        print("❌ ERROR: SHOTSTACK_KEY not found.")
        return

    # 🎥 The "Golden Payload" - This structure is verified
    payload = {
        "timeline": {
            "tracks": [
                {
                    "clips": [
                        {
                            "asset": {
                                "type": "html",
                                "html": "<p style='color: #ffffff; font-size: 40px; text-align: center;'>KFC LAB: PhD Research Support</p>",
                                "width": 1024,
                                "height": 576
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
            "resolution": "sd" 
        }
    }

    url = "https://api.shotstack.io/edit/v1/render"
    headers = {
        "x-api-key": key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 201:
            render_id = response.json().get('response', {}).get('id')
            print(f"✅ 201 SUCCESS: Render ID {render_id}")
            if tg_token:
                requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", 
                             json={"chat_id": chat_id, "text": f"🎬 SUCCESS: Video Render {render_id} started!"})
        else:
            # 🔍 This is the most important part - it will print the EXACT error
            print(f"❌ REJECTION DETAIL: {response.text}")
            
    except Exception as e:
        print(f"❌ SCRIPT CRASH: {e}")

if __name__ == "__main__":
    run_media_production()
