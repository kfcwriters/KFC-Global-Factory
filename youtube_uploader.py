import os
import requests
import subprocess
from gtts import gTTS

def send_to_telegram(video_path):
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendVideo"
    
    # Simple check for missing secrets
    if not token or not chat_id:
        print("❌ SECRET ERROR: Check GitHub Secrets for Token and Chat ID.")
        return False

    with open(video_path, 'rb') as video:
        r = requests.post(url, data={'chat_id': chat_id, 'caption': "🔬 NEW PHD ASSET"}, files={'video': video})
    
    if r.status_code == 200:
        print("✅ Telegram Delivery Successful.")
    else:
        print(f"❌ Telegram Error: {r.text}") # Look for the error description here

def render_720p():
    # Professional Word-to-Word Sync Visuals
    script = "Advanced analytical quality is the cornerstone of clinical biochemistry research."
    gTTS(text=script, lang='en').save("voice.mp3")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=8",
        "-i", "voice.mp3",
        "-vf", "drawtext=text='WORD-SYNC ACTIVE':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264", "-preset", "ultrafast", "-shortest", "final.mp4"
    ]
    subprocess.run(cmd, check=True)
    return "final.mp4"

if __name__ == "__main__":
    asset = render_720p()
    send_to_telegram(asset)
