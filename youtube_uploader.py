import os
import time
import requests

def run_delivery():
    render_id = os.getenv('RENDER_ID')
    api_key = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq"
    
    if not render_id:
        print("❌ No Render ID found.")
        return

    # 🕒 Wait for Shotstack to finish (approx 30 seconds)
    time.sleep(30)
    
    status_url = f"https://api.shotstack.io/edit/v1/render/{render_id}"
    response = requests.get(status_url, headers={"x-api-key": api_key}).json()
    
    video_url = response.get('response', {}).get('url')
    
    if video_url:
        print(f"✅ Video is Ready: {video_url}")
        # 🚀 Here we add the YouTube Upload Logic or Telegram Notification
        # For now, let's send it to your Telegram so you can check it.
        token = os.getenv('TELEGRAM_TOKEN')
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": "1060905337", "text": f"🎬 Video Ready for KFC WRITERS:\n{video_url}"})
    else:
        print("⏳ Video still rendering...")

if __name__ == "__main__":
    run_delivery()
