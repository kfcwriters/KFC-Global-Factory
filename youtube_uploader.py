import os
import random
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_cbme_topic():
    # Elite PhD-level topics to establish authority
    topics = [
        {"t": "SIGMA METRICS", "s": "Welcome to KFC Lab. Today we calibrate analytical performance using Six Sigma metrics to achieve zero-error clinical biochemistry.", "tag": "Quality"},
        {"t": "RENAL BIOMARKERS", "s": "Institutional Update. We are mapping novel serum indicators for early diabetic nephropathy detection and patient monitoring.", "tag": "Nephrology"},
        {"t": "PCR PRINCIPLES", "s": "Molecular Series. Analyzing real-time PCR quantification methods for high-precision diagnostic pathology.", "tag": "Molecular"}
    ]
    return random.choice(topics)

def render_720p(topic):
    print(f"🎬 BROADCAST: Rendering {topic['t']} with AI Voice...")
    
    # 1. Voice Generation (Free/Unlimited)
    tts = gTTS(text=topic['s'], lang='en')
    tts.save("voice.mp3")

    # 2. Institutional Visuals: Navy Blue background, Gold-White high contrast
    # Adding 'drawgrid' for that scientific laboratory feel
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=30",
        "-i", "voice.mp3",
        "-vf", (
            "drawgrid=w=128:h=72:t=1:c=white@0.05, " # Subtle Scientific Grid
            f"drawtext=font='sans':text='PHD SERIES\: {topic['t']}':fontcolor=gold:fontsize=55:x=(w-text_w)/2:y=180, "
            f"drawtext=font='sans':text='{topic['tag']} Specialist View':fontcolor=white:fontsize=32:x=(w-text_w)/2:y=330, "
            "drawtext=font='sans':text='KFC LAB\: BROADCASTING LIVE':fontcolor=0x00FF00:fontsize=22:x=50:y=50"
        ),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "broadcast_asset.mp4"
    ]
    subprocess.run(cmd, check=True)

def upload(topic):
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f"Medical Science Review: {topic['t']}",
                "description": f"PhD-level review of {topic['t']}. Manuscript and Quality support by KFC Lab.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("broadcast_asset.mp4")
    )
    request.execute()
    print(f"✅ Published: {topic['t']}")

if __name__ == "__main__":
    current = get_cbme_topic()
    render_720p(current)
    try: upload(current)
    except Exception as e: print(f"⚠️ Error: {e}")
