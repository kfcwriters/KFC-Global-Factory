import os
import random
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_cbme_topic():
    # Structured teaching segments for keyframing
    topics = [
        {
            "t": "SIGMA METRICS & QC",
            "segments": [
                {"text": "Evaluating Analytical Performance", "start": 0, "end": 10},
                {"text": "Six Sigma: The Gold Standard", "start": 10, "end": 20},
                {"text": "Optimizing Lab Quality Control", "start": 20, "end": 35}
            ],
            "full_script": "Welcome to KFC Lab. Sigma metrics allow us to evaluate the analytical performance of a laboratory. A Six Sigma process is the world-class standard, indicating that your lab results are highly precise. We use this data to optimize quality control frequency and improve total patient safety."
        },
        {
            "t": "LAB AUTOMATION SYSTEMS",
            "segments": [
                {"text": "Integrated Laboratory Workflow", "start": 0, "end": 10},
                {"text": "Pre-Analytical & Analytical Phases", "start": 10, "end": 20},
                {"text": "Reducing Human Error in MLT", "start": 20, "end": 35}
            ],
            "full_script": "Medical Education Series. Automation in the clinical laboratory involves integrated systems that handle pre-analytical and analytical phases. For MBBS and MLT students, it is vital to understand how automation reduces turnaround time and human error. However, internal quality control remains the cornerstone of valid results."
        }
    ]
    return random.choice(topics)

def render_720p(topic):
    print(f"🎬 DYNAMIC RENDER: {topic['t']}...")
    
    # 1. Voice Generation
    tts = gTTS(text=topic['full_script'], lang='en')
    tts.save("voice.mp3")

    # 2. Dynamic Visuals (Text changes over time)
    # Using 'enable' filter to show different text segments at specific times
    filters = []
    for i, seg in enumerate(topic['segments']):
        filters.append(
            f"drawtext=font='sans':text='{seg['text']}':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=350:enable='between(t,{seg['start']},{seg['end']})'"
        )
    
    filter_chain = ",".join(filters)
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=60",
        "-i", "voice.mp3",
        "-vf", (
            f"drawgrid=w=128:h=72:t=1:c=white@0.05, "
            f"drawtext=font='sans':text='PHD SERIES\: {topic['t']}':fontcolor=gold:fontsize=55:x=(w-text_w)/2:y=150, "
            f"{filter_chain}, "
            "drawtext=font='sans':text='KFC LAB\: TEACHING IN PROGRESS':fontcolor=0x00FF00:fontsize=22:x=50:y=50"
        ),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "dynamic_teaching.mp4"
    ]
    subprocess.run(cmd, check=True)

def upload(topic):
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": f"Medical Teaching: {topic['t']}", "categoryId": "27"}, "status": {"privacyStatus": "public"}},
        media_body=MediaFileUpload("dynamic_teaching.mp4")
    )
    request.execute()
    print(f"✅ Published Dynamic Lesson: {topic['t']}")

if __name__ == "__main__":
    current = get_cbme_topic()
    render_720p(current)
    try: upload(current)
    except Exception as e: print(f"⚠️ Error: {e}")
