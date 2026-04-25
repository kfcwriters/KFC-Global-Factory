import os
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_teaching_lecture():
    # High-level PhD content without student references
    topic = "PHD RESEARCH\: SIGMA METRIC ANALYSIS"
    
    # Large, bold segments that change throughout the video
    segments = [
        {"text": "ANALYTICAL PRECISION", "start": 0, "end": 20},
        {"text": "SIGMA CALCULATION", "start": 20, "end": 40},
        {"text": "QUALITY OPTIMIZATION", "start": 40, "end": 60}
    ]

    script = (
        "Welcome to the KFC Lab PhD Series. Today we analyze advanced Sigma Metrics in Clinical Biochemistry. "
        "Laboratory quality is defined by analytical precision and the strategic reduction of total allowable error. "
        "By achieving Six Sigma status, we ensure that clinical results are world-class, providing the highest "
        "level of diagnostic safety for patients. This institutional framework optimizes quality control "
        "and minimizes resource waste across all complex clinical departments."
    )
    
    return {"t": topic, "s": script, "segments": segments}

def render_720p(lecture):
    print(f"🎬 RENDERING: High-Contrast PhD Lecture...")
    
    # 1. Voiceover
    tts = gTTS(text=lecture['s'], lang='en')
    tts.save("master_voice.mp3")

    # 2. Huge Subtitle Filters (Fontsize 120 for maximum visibility)
    filters = []
    for seg in lecture['segments']:
        filters.append(
            f"drawtext=text='{seg['text']}':fontcolor=white:fontsize=120:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.6:enable='between(t,{seg['start']},{seg['end']})'"
        )
    
    filter_chain = ",".join(filters)
    
    # 3. Optimized Render: Using 'ultrafast' to prevent GitHub timeouts
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=62", # Dark Blue
        "-i", "master_voice.mp3",
        "-vf", (
            f"drawgrid=w=100:h=100:t=2:c=white@0.1, "
            f"drawtext=text='{lecture['t']}':fontcolor=gold:fontsize=65:x=(w-text_w)/2:y=100, "
            f"{filter_chain}, "
            "drawtext=text='KFC LAB\: PhD CLINICAL BROADCAST':fontcolor=0x00FF00:fontsize=25:x=50:y=50"
        ),
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "final_lecture.mp4"
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
                "title": "PhD Clinical Series: Sigma Metrics",
                "description": "Scientific review of Sigma Metrics. Quality support by KFC Lab.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("final_lecture.mp4", resumable=True)
    )
    request.execute()
    print("✅ High-Quality PhD Lecture Published.")

if __name__ == "__main__":
    lecture = get_teaching_lecture()
    render_720p(lecture)
    try: upload()
    except Exception as e: print(f"⚠️ Error: {e}")
