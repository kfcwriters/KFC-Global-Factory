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
    print(f"🎬 FFmpeg: Rendering CBME Topic: {topic['title']}")
    
    # Motion Graphic: Text pulses and background shifts
    cmd = (
        f'ffmpeg -y -f lavfi -i "color=c=0x000032:s=1280x720:d=30" '
        f'-f lavfi -i "sine=frequency=400:d=30" '
        f'-vf "drawtext=text=\'CBME SERIES: {topic["title"]}\':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=150, '
        f'drawtext=text=\'{topic["sub"]}\':fontcolor=lightgray:fontsize=35:x=(w-text_w)/2:y=300+10*sin(t*1.5), '
        f'drawtext=text=\'KFC LAB: PhD-LEVEL RESEARCH SUPPORT\':fontcolor=yellow:fontsize=30:x=(w-text_w)/2:y=550" '
        f'-c:v libx264 -pix_fmt yuv420p -c:a aac -shortest medical_cbme.mp4'
    )
    subprocess.run(cmd, shell=True, check=True)

def upload(topic):
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
    
    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f"CBME Medical Series: {topic['title']}",
                "description": f"Exploring {topic['sub']} for MBBS and MLT students. {topic['tag']} focus.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("medical_cbme.mp4")
    )
    request.execute()
    print(f"✅ CBME Asset '{topic['title']}' Published.")

if __name__ == "__main__":
    current_topic = get_random_cbme_topic()
    render_720p(current_topic)
    try: upload(current_topic)
    except Exception as e: print(f"⚠️ Upload error: {e}")
