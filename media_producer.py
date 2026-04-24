import requests

def run_media_production():
    # 🔑 HARDCODED PRODUCTION KEY
    key = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq"
    
    # 📡 THE OFFICIAL PRODUCTION ENDPOINT
    url = "https://api.shotstack.io/edit/v1/render"
    
    # 🔬 BRANDED CONTENT
    title = "KFC LAB: PhD Research Support"
    description = "Specialized medical writing and clinical biochemistry analysis."

    payload = {
        "timeline": {
            "background": "#000000",
            "tracks": [
                {
                    "clips": [
                        {
                            "asset": {
                                "type": "html",
                                "html": f"<div style='color:#00d4ff; font-family:Arial; text-align:center;'><h1>{title}</h1><p style='color:white;'>{description}</p></div>",
                                "css": "div { margin-top: 300px; padding: 20px; border: 1px solid #00d4ff; }"
                            },
                            "start": 0,
                            "length": 6
                        }
                    ]
                }
            ]
        },
        "output": {
            "format": "mp4",
            "resolution": "sd",
            "destinations": [
                {
                    "provider": "youtube",
                    "options": {
                        "title": f"{title} 2026",
                        "description": f"{description} Contact: kfcwriters@gmail.com",
                        "category": "27",
                        "privacy": "public"
                    }
                }
            ]
        }
    }

    print(f"🚀 STUDIO: Sending Production Strike to Shotstack...")
    
    try:
        response = requests.post(url, json=payload, headers={"x-api-key": key, "Content-Type": "application/json"})
        
        print(f"📊 SERVER STATUS: {response.status_code}")
        
        if response.status_code == 201:
            render_id = response.json().get('response', {}).get('id')
            print(f"✅ SUCCESS! Render ID: {render_id}")
            print(f"🔗 View progress: https://dashboard.shotstack.io/renders/{render_id}")
        else:
            print(f"❌ REJECTION DETAIL: {response.text}")
            
    except Exception as e:
        print(f"❌ CRASH: {e}")

if __name__ == "__main__":
    run_media_production()
