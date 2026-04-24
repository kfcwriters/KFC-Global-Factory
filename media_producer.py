import requests

def run_media_production():
    # 🚨 TEMPORARY BYPASS: Paste your actual key between the quotes below
    # Example: key = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq"
    key = "PASTE_YOUR_SHOTSTACK_KEY_HERE"
    
    tg_token = "7052953683:AAFf_WbXl7_Z3o8Vp_K-u0G6UaO-8m-Z1oM" # Your token
    chat_id = "1060905337"

    # 🎥 The most basic payload possible
    payload = {
        "timeline": {
            "tracks": [{"clips": [{"asset": {"type": "title", "text": "TESTING"}, "start": 0, "length": 2}]}]
        },
        "output": {"format": "mp4", "resolution": "sd"}
    }

    url = "https://api.shotstack.io/edit/v1/render"
    headers = {"x-api-key": key, "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"📊 Status: {response.status_code}")
        print(f"📜 Detail: {response.text}") # THIS WILL PRINT THE ACTUAL ERROR
        
        if response.status_code == 201:
            print("✅ SUCCESS!")
    except Exception as e:
        print(f"❌ CRASH: {e}")

if __name__ == "__main__":
    run_media_production()
