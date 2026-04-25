import os
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_teaching_lecture():
    # Elite PhD Clinical Content
    topic = "PHD RESEARCH: SIGMA METRIC ANALYSIS"
    
    # Perfectly timed subtitles for 10-second segments
    segments = [
        {"text": "ANALYTICAL PRECISION", "start": 0, "end": 10},
        {"text": "REDUCING TOTAL ERROR", "start": 10, "end": 20},
        {"text": "WORLD-CLASS SIX SIGMA", "start": 20, "end": 30},
        {"text": "INSTITUTIONAL QUALITY", "start": 30, "end": 42}
    ]

    script = (
        "Welcome to the KFC Lab PhD series. Laboratory quality is defined by analytical precision and "
        "the reduction of total allowable error. By achieving Six Sigma status, we ensure that clinical "
        "results are world-class, providing the highest level of diagnostic safety for patients and "
        "achieving institutional excellence in clinical biochemistry."
    )
    
    return {"t": topic, "s": script, "segs": segments}

def render_720p(lecture):
    print(f"🎬 RENDERING: Synced PhD Masterclass for {lecture['t']}...")
    
    # 1. Voiceover
    tts = gTTS(text=lecture['s'], lang='en')
    tts.save("master_voice.mp3")

    # 2. Build the Visual Overlays (Decent size subtitles)
    filters = []
    for s in lecture['segs']:
        filters.append(
            f"drawtext=text='{s['text']}':fontcolor=white:fontsize=75:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.6:enable='between(t,{s['start']},{s['end']})'"
        )
    
    filter_chain = ",".join(filters)
    
    # 3. Secure Render: Dark Blue background
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=42",
        "-i", "master_voice.mp3",
        "-vf", (
            f"drawgrid=w=100:h=100:t=2:c=white@0.1, "
            f"drawtext=text='{lecture['t']}':fontcolor=gold:fontsize=50:x=(w-text_w)/2:y=100, "
            f"{filter_chain}, "
            "drawtext=text='KFC LAB: PhD CLINICAL BROADCAST':fontcolor=green:fontsize=25:x=50:y=50"
        ),
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "synced_lecture.mp4"
    ]
    subprocess.run(cmd, check=True)

def upload():
    # Uses resumable upload to handle larger files better
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
    youtube = build("youtube", "v3", credentials=creds)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": "PhD Clinical Masterclass", "categoryId": "27"}, "status": {"privacyStatus": "public"}},
        media_body=MediaFileUpload("synced_lecture.mp4", resumable=True)
    )
    request.execute()
    print("✅ Synced PhD Masterclass Published.")

if __name__ == "__main__":
    lecture = get_teaching_lecture()
    render_720p(lecture)
    try: upload()
    except Exception as e: print(f"⚠️ Error: {e}")
