import os
import requests

def run_media_production():
    # 🚨 HARDCODED KEY TEST (Bypassing GitHub Secrets)
    # Replace the text below with your actual Shotstack key
    key = "PASTE_YOUR_SHOTSTACK_PRODUCTION_KEY_HERE"
    
    url = "https://api.shotstack.io/edit/v1/render"
    
    payload = {
        "timeline": {
            "tracks": [{"clips": [{"asset": {"type": "title", "text": "KFC LAB TEST"}, "start": 0, "length": 2}]}]
        },
        "output": {"format": "mp4", "resolution": "sd"}
    }

    print(f"📡 Sending request to Shotstack...")
    
    try:
        response = requests.post(url, json=payload, headers={"x-api-key": key, "Content-Type": "application/json"})
        
        # 📊 THIS IS THE ONLY LINE THAT MATTERS NOW
        print(f"📊 SERVER RESPONSE STATUS: {response.status_code}")
        print(f"📜 SERVER ERROR MESSAGE: {response.text}")
        
        if response.status_code == 201:
            print("✅ SUCCESS! Check your dashboard now.")
            
    except Exception as e:
        print(f"❌ SCRIPT ERROR: {e}")

if __name__ == "__main__":
    run_media_production()
