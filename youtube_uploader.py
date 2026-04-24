import os
import requests

def upload_to_youtube(video_url, title):
    # This uses a standard webhook or YouTube's direct API
    # Since we are in 'Synthetic Factory' mode, we will use your Telegram 
    # to send you the direct download link for manual one-click upload 
    # until the API handshake is finalized.
    
    tg_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = "1060905337"
    
    msg = f"🎬 NEW VIDEO READY FOR YOUTUBE\n\nTopic: {title}\n🔗 Download Link: {video_url}\n\nCEO Action: Download and post to KFC WRITERS Channel."
    
    if tg_token:
        requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": chat_id, "text": msg})
        print("📲 Telegram notified with video link.")

# This is called by your main factory
if __name__ == "__main__":
    # Logic to get the latest render link from Shotstack
    print("🚀 Youtube Uploader Agent Active.")
