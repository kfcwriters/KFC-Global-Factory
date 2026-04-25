import os
import random
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_random_cbme_topic():
    topics = [
        {"title": "Bilirubin Metabolism", "sub": "Jaundice Types & Van Den Bergh Test", "tag": "Biochemistry"},
        {"title": "Renal Function", "sub": "GFR & Creatinine Clearance Principles", "tag": "Physiology"},
        {"title": "Anemia Classification", "sub": "Microcytic vs Macrocytic Morphology", "tag": "Hematology"},
        {"title": "Lab Quality", "sub": "Levey-Jennings Charts & Westgard Rules", "tag": "Quality Control"}
    ]
    return random.choice(topics)

def render_720p(topic):
    print(f"🎬 FFmpeg: Rendering Educational Asset: {topic['title']}")
    
    # We use a solid white background with black/blue text for 100% visibility
    # We use a steady 'sine' tone so there is definitely audio
    t1 = f"MEDICAL TEACHING: {topic['title']}"
    t2 = f"Clinical Key: {topic['sub']}"
    t3 = "Support: kfcwriters@gmail.com"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=white:s=1280x720:d=30",
        "-f", "lavfi", "-i", "sine=f=440:d=30",
        "-vf", f"drawtext=font='sans':text='{t1}':fontcolor=blue:fontsize=50:x=(w-text_w)/2:y=150,"
               f"drawtext=font='sans':text='{t2}':fontcolor=black:fontsize=35:x=(w-text_w)/2:y=350,"
               f"drawtext=font='sans':text='{t3}':fontcolor=red:fontsize=30:x=(w-text_w)/2:y=600",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest", "medical_teaching.mp4"
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
                "title": f"CBME Medical Lecture: {topic['title']}",
                "description": f"Curriculum review on {topic['sub']}. Support by KFC Lab.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("medical_teaching.mp4")
    )
    request.execute()
    print(f"✅ Published: {topic['title']}")

if __name__ == "__main__":
    current = get_random_cbme_topic()
    render_720p(current)
    try: upload(current)
    except Exception as e: print(f"⚠️ Error: {e}")
