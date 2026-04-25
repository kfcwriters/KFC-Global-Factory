import os
import random
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_cbme_topic():
    # Long-form scripts to ensure 30-45 second teaching videos
    topics = [
        {
            "t": "SIGMA METRICS IN BIOCHEMISTRY", 
            "s": "Welcome to KFC Lab. Today we explore Six Sigma metrics in clinical biochemistry. Sigma metrics allow us to evaluate the analytical performance of a laboratory by measuring defects per million opportunities. A Six Sigma process is the world-class standard, indicating that your lab results are highly precise with minimal errors. We use this to optimize quality control frequency and improve patient safety.", 
            "tag": "Quality Control"
        },
        {
            "t": "DIABETIC NEPHROPATHY MARKERS", 
            "s": "Institutional Update on Clinical Biomarkers. Diabetic nephropathy is a leading cause of chronic kidney disease. We are currently researching novel serum biomarkers like Myonectin and GPLD1 to detect early-stage renal damage before significant microalbuminuria occurs. Understanding these molecular manifestations is essential for effective clinical management and preventing long-term diabetic complications.", 
            "tag": "Nephrology"
        },
        {
            "t": "LABORATORY AUTOMATION SYSTEMS", 
            "s": "Medical Education Series on Lab Automation. Automation in the clinical laboratory involves integrated systems that handle pre-analytical, analytical, and post-analytical phases. For MBBS and MLT students, it is vital to understand how Total Laboratory Automation reduces turnaround time and human error. However, internal quality control remains the cornerstone of ensuring that automated results are medically valid.", 
            "tag": "Clinical Lab"
        }
    ]
    return random.choice(topics)

def render_720p(topic):
    print(f"🎬 TEACHING RENDER: Generating {topic['t']}...")
    
    # 1. Voice Generation (Extended Script)
    tts = gTTS(text=topic['s'], lang='en')
    tts.save("voice.mp3")

    # 2. Institutional Visuals with Data Grid
    # We remove the '-shortest' tag to ensure the video plays the full audio script
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=60", # Buffer 60s
        "-i", "voice.mp3",
        "-vf", (
            "drawgrid=w=128:h=72:t=1:c=white@0.05, "
            f"drawtext=font='sans':text='PHD SERIES\: {topic['t']}':fontcolor=gold:fontsize=50:x=(w-text_w)/2:y=150, "
            f"drawtext=font='sans':text='Institutional Research':fontcolor=white:fontsize=30:x=(w-text_w)/2:y=300, "
            "drawtext=font='sans':text='KFC LAB\: TEACHING IN PROGRESS':fontcolor=0x00FF00:fontsize=22:x=50:y=50"
        ),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "teaching_asset.mp4"
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
                "title": f"Medical Teaching: {topic['t']}",
                "description": f"Curriculum review on {topic['t']}. PhD-level manuscript support by KFC Lab.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("teaching_asset.mp4")
    )
    request.execute()
    print(f"✅ Published Professional Lecture: {topic['t']}")

if __name__ == "__main__":
    current = get_cbme_topic()
    render_720p(current)
    try: upload(current)
    except Exception as e: print(f"⚠️ Error: {e}")
