import os
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_synced_phd_content():
    topic = "PHD RESEARCH: SIGMA METRIC ANALYSIS"
    
    # Precise timing for every word/phrase to ensure perfect sync
    sync_segs = [
        {"word": "WELCOME TO THE LAB", "start": 0, "end": 4},
        {"word": "PHD SERIES: SIGMA METRICS", "start": 4, "end": 9},
        {"word": "DEFINING ANALYTICAL PRECISION", "start": 9, "end": 14},
        {"word": "FOR INSTITUTIONAL EXCELLENCE", "start": 14, "end": 20}
    ]

    script = "Welcome to the lab. PhD Series: Sigma Metrics. Defining analytical precision for institutional excellence."
    return {"t": topic, "s": script, "sync": sync_segs}

def render_720p(content):
    print(f"🎬 RENDERING: Frame-Level Word-Synced PhD Asset...")
    
    # 1. Voiceover
    tts = gTTS(text=content['s'], lang='en')
    tts.save("master_voice.mp3")

    # 2. Build the Sync-Filter (Centered, Decent Size, High Contrast)
    filters = []
    for s in content['sync']:
        filters.append(
            f"drawtext=text='{s['word']}':fontcolor=white:fontsize=85:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.7:enable='between(t,{s['start']},{s['end']})'"
        )
    
    filter_chain = ",".join(filters)
    
    # 3. Secure Render: Dark Blue Scientific Grid
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=21", # Match script length
        "-i", "master_voice.mp3",
        "-vf", (
            f"drawgrid=w=100:h=100:t=2:c=white@0.1, "
            f"drawtext=text='KFC LAB BROADCAST':fontcolor=gold:fontsize=30:x=50:y=50, "
            f"{filter_chain}"
        ),
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "final_synced.mp4"
    ]
    subprocess.run(cmd, check=True)

def upload():
    # Note: If you hit the daily limit, this will fail until the 24h reset
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
    youtube = build("youtube", "v3", credentials=creds)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": "PhD Clinical Masterclass (Word-Synced)", "categoryId": "27"}, "status": {"privacyStatus": "public"}},
        media_body=MediaFileUpload("final_synced.mp4", resumable=True)
    )
    request.execute()
    print("✅ High-Precision Word-Synced Asset Published.")

if __name__ == "__main__":
    content = get_synced_phd_content()
    render_720p(content)
    try: upload()
    except Exception as e: print(f"⚠️ Upload Status: {e}")
