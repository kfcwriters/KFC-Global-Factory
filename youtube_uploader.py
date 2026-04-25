import os
import random
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_random_cbme_topic():
    topics = [
        {"title": "Enzyme Inhibition", "sub": "Competitive vs Non-Competitive Kinetics", "tag": "Biochemistry"},
        {"title": "Acid-Base Balance", "sub": "Anion Gap & Metabolic Acidosis", "tag": "Physiology"},
        {"title": "Molecular Diagnostics", "sub": "PCR Principles & Real-Time Quantification", "tag": "Pathology"},
        {"title": "Quality Management", "sub": "Six Sigma Metrics in Clinical Labs", "tag": "Lab Medicine"},
        {"title": "Hormonal Regulation", "sub": "Thyroid Function & Feedback Loops", "tag": "Endocrinology"}
    ]
    return random.choice(topics)

def render_720p(topic):
    print(f"🎬 FFmpeg: Force-Rendering 30s Visual Script for {topic['title']}...")
    
    # Path to the guaranteed font on GitHub Actions runners
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    
    # Force duration 30s, add professional medical hum, and FORCE visible text
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=30", # Dark Medical Blue
        "-f", "lavfi", "-i", "cosinetone=f=150:d=30", # Deep Medical Hum (No Beeps)
        "-vf", f"drawtext=fontfile={font_path}:text='CBME SERIES\: {topic['title']}':fontcolor=white:fontsize=55:x=(w-text_w)/2:y=150,"
               f"drawtext=fontfile={font_path}:text='{topic['sub']}':fontcolor=yellow:fontsize=38:x=(w-text_w)/2:y=350,"
               f"drawtext=fontfile={font_path}:text='KFC LAB\: PhD RESEARCH SUPPORT':fontcolor=white:fontsize=30:x=(w-text_w)/2:y=600",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        "medical_cbme.mp4"
    ]
    
    subprocess.run(cmd, check=True)
    print("✅ Video/Audio/Script Layered and Synchronized.")

def upload(topic):
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    if not all([token, client_id, client_secret]):
        print("⚠️ Missing Secrets.")
        return

    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=client_id, client_secret=client_secret)
    
    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f"CBME Medical Series: {topic['title']}",
                "description": f"Curriculum review: {topic['sub']}. Professional PhD support by KFC Lab.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("medical_cbme.mp4")
    )
    request.execute()
    print(f"✅ Published with Visuals: {topic['title']}")

if __name__ == "__main__":
    current_topic = get_random_cbme_topic()
    render_720p(current_topic)
    try: upload(current_topic)
    except Exception as e: print(f"⚠️ Error: {e}")
