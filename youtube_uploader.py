import os
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_masterclass_lecture():
    # High-level PhD script without any mention of students
    topic = "PHD MASTERCLASS\: ANALYTICAL SIGMA METRICS"
    
    # We use huge, bold subtitles that change throughout the 5 minutes
    segments = [
        {"text": "PHD QUALITY STANDARDS", "start": 0, "end": 100},
        {"text": "TOTAL ALLOWABLE ERROR", "start": 100, "end": 200},
        {"text": "WORLD-CLASS SIX SIGMA", "start": 200, "end": 305}
    ]

    script = (
        "Welcome to the KFC Lab PhD Clinical Series. Today we analyze advanced Sigma Metrics in Clinical Biochemistry. "
        "Laboratory quality is defined by analytical precision and the strategic reduction of total allowable error. "
        "By achieving Six Sigma status, we ensure that clinical results are world-class, providing the highest "
        "level of diagnostic safety for patients worldwide. This institutional framework optimizes quality control "
        "and minimizes resource waste across all complex clinical departments. We are establishing the boundary "
        "between a valid result and potential diagnostic error by aligning internal control with external data."
    )
    
    return {"t": topic, "s": script, "segments": segments}

def render_720p(lecture):
    print(f"🎬 RENDERING: 5-Minute Mega-Visual PhD Masterclass...")
    
    # 1. Voiceover (Free & Unlimited)
    tts = gTTS(text=lecture['s'], lang='en')
    tts.save("master_voice.mp3")

    # 2. Huge Subtitle Filters (Fontsize 100 for maximum clarity)
    filters = []
    for seg in lecture['segments']:
        filters.append(
            f"drawtext=text='{seg['text']}':fontcolor=white:fontsize=100:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.5:enable='between(t,{seg['start']},{seg['end']})'"
        )
    
    filter_chain = ",".join(filters)
    
    # 3. Optimized 5-Minute Render: Mandelbrot background for visual stability
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "mandelbrot=s=1280x720:rate=25:d=305", # Moving Pattern (No black screen)
        "-i", "master_voice.mp3",
        "-vf", (
            f"drawgrid=w=100:h=100:t=2:c=white@0.1, "
            f"drawtext=text='{lecture['t']}':fontcolor=gold:fontsize=65:x=(w-text_w)/2:y=100, "
            f"{filter_chain}, "
            "drawtext=text='KFC LAB\: PhD CLINICAL BROADCAST':fontcolor=0x00FF00:fontsize=25:x=50:y=50"
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
        body={
            "snippet": {
                "title": "PhD Clinical Masterclass: Sigma Metrics",
                "description": "Comprehensive 5-minute review of Sigma Metrics. Support by KFC Lab.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("final_masterclass.mp4", resumable=True)
    )
    request.execute()
    print("✅ 5-Minute Masterclass Published with Huge Visuals.")

if __name__ == "__main__":
    lecture = get_masterclass_lecture()
    render_720p(lecture)
    try: upload()
    except Exception as e: print(f"⚠️ Error: {e}")
