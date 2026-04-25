import os
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_synced_lecture():
    # Elite PhD script - no student references
    topic = "PHD RESEARCH: SIGMA METRIC ANALYSIS"
    
    # We define the text timing for word-level alignment
    segments = [
        {"text": "WELCOME TO THE LAB", "start": 0, "end": 5},
        {"text": "ADVANCED SIGMA METRICS", "start": 5, "end": 15},
        {"text": "ANALYTICAL PRECISION", "start": 15, "end": 25},
        {"text": "WORLD-CLASS STANDARDS", "start": 25, "end": 38}
    ]

    script = (
        "Welcome to the KFC Lab PhD series. Today we analyze advanced Sigma Metrics in Clinical Biochemistry. "
        "Analytical precision and the reduction of total allowable error are our primary focus. "
        "By achieving Six Sigma status, we ensure that clinical results are world-class, providing the highest "
        "level of diagnostic safety for patients and institutional excellence."
    )
    
    return {"t": topic, "s": script, "segs": segments}

def render_720p(lecture):
    print(f"🎬 RENDERING: Word-Aligned PhD Masterclass...")
    
    # 1. Voiceover
    tts = gTTS(text=lecture['s'], lang='en')
    tts.save("master_voice.mp3")

    # 2. Build the Sync-Filter (Decent size, no escape errors)
    filters = []
    for s in lecture['segs']:
        filters.append(
            f"drawtext=text='{s['text']}':fontcolor=white:fontsize=75:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.6:enable='between(t,{s['start']},{s['end']})'"
        )
    
    filter_chain = ",".join(filters)
    
    # 3. Secure Render: Dark Blue background with a grid
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=40",
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
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
    youtube = build("youtube", "v3", credentials=creds)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "PhD Clinical Masterclass: Sigma Metrics",
                "description": "Synced Word-to-Word PhD Review. Support by KFC Lab.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("synced_lecture.mp4", resumable=True)
    )
    request.execute()
    print("✅ Synced PhD Masterclass Published.")

if __name__ == "__main__":
    lecture = get_synced_lecture()
    render_720p(lecture)
    try: upload()
    except Exception as e: print(f"⚠️ Error: {e}")
