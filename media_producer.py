import os
import requests

def run_media_production():
    # Use the key you provided directly to be safe
    key = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq"
    
    # 🚨 THE SECRET: Using the 'stage' endpoint is often more stable for trial keys
    url = "https://api.shotstack.io/v1/render"
    
    # Absolute bare-minimum payload
    payload = {
        "timeline": {
            "tracks": [{
                "clips": [{
                    "asset": {"type": "title", "text": "KFC"},
                    "start": 0, "length": 1
                }]
            }]
        },
        "output": {"format": "mp4", "resolution": "sd"}
    }

    headers = {"x-api-key": key, "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        # This will print the status AND the full error message
        print(f"STATUS: {response.status_code}")
        print(f"REASON: {response.text}")
    except Exception as e:
        print(f"CRASH: {e}")

if __name__ == "__main__":
    run_media_production()
