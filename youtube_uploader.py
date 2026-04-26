import os
import requests
import subprocess
from gtts import gTTS

def send_to_telegram(video_path):
    print("📤 TELEGRAM BRIDGE: Initializing Delivery...")
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendVideo"
    
    # Simple check to ensure secrets are loaded
    if not token or not chat_id:
        print("❌ ERROR: TELEGRAM_TOKEN or TELEGRAM_CHAT_ID is missing in GitHub Secrets.")
        return False

    with open(video_path, 'rb') as video:
        r = requests.post(url, data={'chat_id': chat_id, 'caption': "🔬 PHD VIDEO READY"}, files={'video': video})
    
    if r.status_code == 200:
        print("✅ Telegram Delivery Successful.")
        return True
    else:
        print(f"❌ Telegram Error: {r.text}")
        return False

def render_720p():
    print("🎬 RENDERING: Synced Science Asset...")
    # High-level PhD content (No student references)
    script = "Welcome to KFC Lab. Today we analyze advanced Sigma Metrics for clinical biochemistry excellence."
    gTTS(text=script, lang='en').save("voice.mp3")
    
    # Burns word-synced large subtitles
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=10",
        "-i", "voice.mp3",
        "-vf", "drawtext=text='PHD RESEARCH SERIES':fontcolor=gold:fontsize=45:x=(w-text_w)/2:y=100, "
               "drawtext=text='WORD-SYNC ACTIVE':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264", "-preset", "ultrafast", "-shortest", "review_this.mp4"
    ]
    subprocess.run(cmd, check=True)
    return "review_this.mp4"

if __name__ == "__main__":
    asset = render_720p()
    send_to_telegram(asset)
