import os
import requests

def run_media_production():
    # 🧪 TEST 1: We pull the key, but we also print a 'Masked' version to the log 
    # so you can see if GitHub is actually providing it.
    key = os.getenv('SHOTSTACK_KEY')
    tg_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337"

    if not key:
        print("❌ CRITICAL: SHOTSTACK_KEY is empty in GitHub Secrets!")
        return
    else:
        print(f"🔑 Key Detected: {key[:4]}***{key[-4:]}")

    # 🎥 TEST 2: The absolute minimum payload possible.
    # No destinations, no HTML, no CSS. Just a title.
    payload = {
        "timeline": {
            "tracks": [{
                "clips": [{
                    "asset": {"type": "title", "text": "KFC LAB TEST"},
                    "start": 0, "length": 2
                }]
            }]
        },
        "output": {"format": "mp4", "resolution": "720"}
    }

    # 🌐 TEST 3: Correcting the Endpoint
    # Some accounts require the 'v1' or 'stage' endpoint. We will use v1.
    url = "https://api.shotstack.io/edit/v1/render"
    headers = {"x-api-key": key, "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"📡 Request Sent to: {url}")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ 201 SUCCESS: Render is live!")
        else:
            # THIS WILL TELL US EXACTLY WHY IT IS 400
            print(f"❌ REJECTION DETAIL: {response.text}")
            
    except Exception as e:
        print(f"❌ SCRIPT CRASH: {e}")

if __name__ == "__main__":
    run_media_production()
