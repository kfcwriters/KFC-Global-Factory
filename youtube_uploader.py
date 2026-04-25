import os
import random
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_cbme_topic():
    topics = [
        {"t": "Sigma Metrics", "s": "Welcome to KFC Lab. We are analyzing analytical quality via Six Sigma metrics to reduce clinical errors.", "cat": "Quality Control"},
        {"t": "Diabetic Nephropathy", "s": "Institutional Update. We are investigating novel serum biomarkers for early chronic kidney disease detection.", "cat": "Biochemistry"},
        {"t": "Lab Automation", "s": "Medical Education Series. Exploring automation principles for MBBS and MLT students.", "cat": "Education"}
    ]
    return random.choice(topics)

def render_720p(topic):
    print(f"🎬 RENDER: Generating {topic['t']} with Voice...")
    
    # Generate Free Voiceover
    tts = gTTS(text=topic['s'], lang='en')
    tts.save("voice.mp3")

    # Hard-Burn visuals: Navy Blue, Gold text, and a Scientific Grid
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=30",
        "-i", "voice.mp3",
        "-vf", (
            "drawgrid=w=100:h=100:t=1:c=white@0.1, "
            f"drawtext=font='sans':text='PHD RESEARCH\: {topic['t']}':fontcolor=gold:fontsize=55:x=(w-text_w)/2:y=150, "
            f"drawtext=font='sans':text='{topic['cat']} Focus':fontcolor=white:fontsize=30:x=(w-text_w)/2:y=300, "
            "drawtext=font='sans':text='KFC LAB\: CLINICAL BROADCAST':fontcolor=yellow:fontsize=25:x=50:y=50"
        ),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "institutional_asset.mp4"
    ]
    subprocess.run(cmd, check=True)

def upload(topic):
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": f"PhD Lab Update: {topic['t']}", "categoryId": "27"}, "status": {"privacyStatus": "public"}},
        media_body=MediaFileUpload("institutional_asset.mp4")
    )
    request.execute()

if __name__ == "__main__":
    current = get_cbme_topic()
    render_720p(current)
    try: upload(current)
    except Exception as e: print(f"⚠️ Error: {e}")
