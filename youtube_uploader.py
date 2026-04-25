import os
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_5min_lecture():
    topic = "PHD RESEARCH\: SIGMA METRICS"
    # Large subtitle segments
    segments = [
        {"text": "PHD QUALITY STANDARDS", "start": 0, "end": 100},
        {"text": "TOTAL ALLOWABLE ERROR", "start": 100, "end": 200},
        {"text": "WORLD-CLASS SIX SIGMA", "start": 200, "end": 305}
    ]
    script = (
        "Welcome to the KFC Lab PhD Series. Today we analyze advanced Sigma Metrics in Clinical Biochemistry. "
        "Laboratory quality is defined by analytical precision and the reduction of total allowable error. "
        "By achieving Six Sigma status, we ensure that clinical results are world-class, providing the highest "
        "level of diagnostic safety for patients. This institutional framework optimizes quality control and "
        "minimizes resource waste across all clinical departments."
    )
    return {"t": topic, "s": script, "segments": segments}

def render_720p(lecture):
    print(f"🎬 RENDERING: 5-Minute High-Contrast Lecture...")
    
    # 1. Voiceover
    tts = gTTS(text=lecture['s'], lang='en')
    tts.save("master_voice.mp3")

    # 2. Huge Subtitle Filters
    # Using 'fontsize=80' for maximum visibility
    filters = []
    for seg in lecture['segments']:
        filters.append(
            f"drawtext=text='{seg['text']}':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{seg['start']},{seg['end']})'"
        )
    filter_chain = ",".join(filters)
    
    # 3. Secure Render Command (Stable Background)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=305",
        "-i", "master_voice.mp3",
        "-vf", (
            f"drawgrid=w=128:h=72:t=2:c=white@0.1, "
            f"drawtext=text='{lecture['t']}':fontcolor=gold:fontsize=60:x=(w-text_w)/2:y=100, "
            f"{filter_chain}, "
            "drawtext=text='KFC LAB\: PhD BROADCAST':fontcolor=green:fontsize=30:x=50:y=50"
        ),
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "final_masterclass.mp4"
    ]
    subprocess.run(cmd, check=True)

def upload():
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": "PhD Clinical Masterclass", "categoryId": "27"}, "status": {"privacyStatus": "public"}},
        media_body=MediaFileUpload("final_masterclass.mp4", resumable=True)
    )
    request.execute()
    print("✅ 5-Minute Masterclass Published.")

if __name__ == "__main__":
    lecture = get_5min_lecture()
    render_720p(lecture)
    try: upload()
    except Exception as e: print(f"⚠️ Error: {e}")
