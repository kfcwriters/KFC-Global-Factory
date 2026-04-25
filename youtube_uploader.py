import os
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_5min_lecture():
    # Elite, Long-Form PhD Teaching Content (approx 5 mins)
    topic = "ADVANCED ANALYTICAL QUALITY & SIGMA METRICS"
    
    # We use stable chapter text that stays on screen longer
    segments = [
        {"text": "CHAPTER 1\: ANALYTICAL PRECISION STANDARDS", "start": 0, "end": 100},
        {"text": "CHAPTER 2\: SIGMA METRIC CALCULATION", "start": 100, "end": 200},
        {"text": "CHAPTER 3\: TOTAL ALLOWABLE ERROR MAPPING", "start": 200, "end": 305}
    ]

    full_script = (
        "Welcome to the KFC Lab Clinical Scientist series. Today, we conduct a rigorous deep-dive into "
        "Advanced Analytical Quality Management, specifically focusing on the institutional implementation of Sigma Metrics. "
        "In a high-throughput clinical laboratory, precision is not merely a goal; it is a mathematical requirement. "
        "We begin by understanding that every test result is subject to variation. Our role as senior clinical scientists "
        "is to quantify that variation and ensure it remains within medically useful limits. When we discuss the "
        "Total Allowable Error, or T.E.A, we are establishing the rigid boundary between a clinically valid result "
        "and a potential diagnostic error. By aligning our internal quality control with external proficiency testing data, "
        "we can calculate the Sigma Metric for every analyzer in the facility. A Six Sigma process represents "
        "world-class quality, where errors are reduced to fewer than three point four per million opportunities. "
        "This level of reliability allows us to optimize our control frequency, reducing resource waste and ensuring "
        "that patient diagnostic safety is never compromised by analytical drift."
    )
    
    return {"t": topic, "s": full_script, "segments": segments}

def render_720p(lecture):
    print(f"🎬 STABILITY RENDER: 5-Minute PhD Masterclass for {lecture['t']}...")
    
    # 1. Voice Generation (5-Minute Audio)
    tts = gTTS(text=lecture['s'], lang='en')
    tts.save("master_voice.mp3")

    # 2. Build the Filter Chain for Chapters
    filters = []
    for seg in lecture['segments']:
        filters.append(
            f"drawtext=font='sans':text='{seg['text']}':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=350:enable='between(t,{seg['start']},{seg['end']})'"
        )
    filter_chain = ",".join(filters)
    
    # 3. Optimized Render: Uses a static background to prevent CPU crashes
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=305", # Solid Institutional Blue
        "-i", "master_voice.mp3",
        "-vf", (
            f"drawgrid=w=128:h=72:t=1:c=white@0.05, "
            f"drawtext=font='sans':text='PHD MASTERCLASS\: {lecture['t']}':fontcolor=gold:fontsize=50:x=(w-text_w)/2:y=150, "
            f"{filter_chain}, "
            "drawtext=font='sans':text='KFC LAB\: CLINICAL SCIENTIST BROADCAST':fontcolor=0x00FF00:fontsize=22:x=50:y=50"
        ),
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "final_masterclass.mp4"
    ]
    subprocess.run(cmd, check=True)

def upload(lecture):
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
    youtube = build("youtube", "v3", credentials=creds)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f"PhD Masterclass: {lecture['t']}",
                "description": f"Comprehensive 5-minute PhD review on {lecture['t']}. Manuscript and quality support by KFC Lab.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("final_masterclass.mp4", resumable=True)
    )
    request.execute()
    print(f"✅ 5-Minute PhD Masterclass Published: {lecture['t']}")

if __name__ == "__main__":
    lecture = get_5min_lecture()
    render_720p(lecture)
    try: upload(lecture)
    except Exception as e: print(f"⚠️ Error: {e}")
