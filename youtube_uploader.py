import os
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_synced_phd_content():
    # Elite PhD-level content (No student references)
    topic = "PHD RESEARCH: SIGMA METRIC ANALYSIS"
    
    # Precise word-for-word timing segments
    sync_segs = [
        {"word": "WELCOME TO THE LAB", "start": 0, "end": 4},
        {"word": "PHD SERIES: SIGMA METRICS", "start": 4, "end": 9},
        {"word": "ANALYTICAL PRECISION", "start": 9, "end": 14},
        {"word": "WORLD-CLASS STANDARDS", "start": 14, "end": 20}
    ]
    script = "Welcome to the lab. PhD Series: Sigma Metrics. Analytical precision for world-class standards."
    return {"t": topic, "s": script, "sync": sync_segs}

def render_720p(content):
    print("🎬 RENDERING: Professional Word-Synced PhD Asset...")
    tts = gTTS(text=content['s'], lang='en')
    tts.save("master_voice.mp3")

    # Build High-Precision Filters (Fontsize 70: Decent & Clear)
    filters = []
    for s in content['sync']:
        filters.append(
            f"drawtext=text='{s['word']}':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.6:enable='between(t,{s['start']},{s['end']})'"
        )
    filter_chain = ",".join(filters)
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=21",
        "-i", "master_voice.mp3",
        "-vf", f"drawgrid=w=100:h=100:t=2:c=white@0.1, drawtext=text='KFC LAB':fontcolor=gold:fontsize=30:x=50:y=50, {filter_chain}",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "final_synced.mp4"
    ]
    subprocess.run(cmd, check=True)

def upload():
    # Will resume successfully once the 24h YouTube limit resets
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
    youtube = build("youtube", "v3", credentials=creds)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": "PhD Masterclass (Synced)", "categoryId": "27"}, "status": {"privacyStatus": "public"}},
        media_body=MediaFileUpload("final_synced.mp4", resumable=True)
    )
    request.execute()
    print("✅ Word-Synced Asset Published.")

if __name__ == "__main__":
    content = get_synced_phd_content()
    render_720p(content)
    try: upload()
    except Exception as e: print(f"⚠️ Upload Status (Limit Check): {e}")
