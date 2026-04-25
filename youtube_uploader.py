import os
import random
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_teaching_content():
    topics = [
        {"title": "NEUROLOGY: Cranial Nerves", "sub": "Clinical Localization of Lesions"},
        {"title": "ONCOLOGY: Tumor Markers", "sub": "Diagnostic Value of CEA and AFP"},
        {"title": "CARDIOLOGY: Heart Sounds", "sub": "S1 to S4 Auscultation Principles"},
        {"title": "SURGERY: Aseptic Technique", "sub": "Sterilization vs Disinfection Protocol"}
    ]
    return random.choice(topics)

def render_720p(topic):
    print(f"🎬 FFmpeg: Hard-Burning Visuals for {topic['title']}...")
    
    # We use a white background and high-contrast blue text
    # The 'force_style' ensures the text is large and visible
    t1 = topic['title']
    t2 = topic['sub']
    t3 = "PhD Support: kfcwriters@gmail.com"

    # SINGLE-PASS HARD BURN COMMAND
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=white:s=1280x720:d=30", # Background
        "-f", "lavfi", "-i", "sine=f=440:d=30", # Audio
        "-vf", f"drawtext=text='{t1}':fontcolor=0x000080:fontsize=60:x=(w-text_w)/2:y=200,"
               f"drawtext=text='{t2}':fontcolor=black:fontsize=40:x=(w-text_w)/2:y=350,"
               f"drawtext=fontcolor=red:text='{t3}':fontsize=35:x=(w-text_w)/2:y=600",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "final_teaching.mp4"
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
                "title": f"Medical Science Review: {topic['title']}",
                "description": f"Review of {topic['sub']}. PhD manuscript support by KFC Lab.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("final_teaching.mp4")
    )
    request.execute()
    print(f"✅ Published Hard-Burn Asset: {topic['title']}")

if __name__ == "__main__":
    content = get_teaching_content()
    render_720p(content)
    try: upload(content)
    except Exception as e: print(f"⚠️ Error: {e}")
