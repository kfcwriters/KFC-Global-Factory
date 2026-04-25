import os
import random
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def get_random_cbme_topic():
    # Curriculum-based topics to target MBBS/MLT audience
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
    
    # - Using Hex #D3D3D3 to fix the 'lightgray' error
    # - Escaping colons (\:) for internal FFmpeg logic
    # - sin(t*1.5) creates professional floating motion for the subtitle
    cmd = (
        f'ffmpeg -y -f lavfi -i "color=c=0x000032:s=1280x720:d=30" '
        f'-f lavfi -i "sine=frequency=400:d=30" '
        f'-vf "drawtext=text=\'CBME SERIES\: {topic["title"]}\':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=150, '
        f'drawtext=text=\'{topic["sub"]}\':fontcolor=#D3D3D3:fontsize=35:x=(w-text_w)/2:y=300+10*sin(t*1.5), '
        f'drawtext=text=\'KFC LAB\: PhD-LEVEL RESEARCH SUPPORT\':fontcolor=yellow:fontsize=30:x=(w-text_w)/2:y=550" '
        f'-c:v libx264 -pix_fmt yuv420p -c:a aac -shortest medical_cbme.mp4'
    )
    subprocess.run(cmd, shell=True, check=True)

def upload(topic):
    # Pulling keys from your GitHub Secrets vault
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    if not all([token, client_id, client_secret]):
        print("⚠️ Missing YouTube Auth Secrets. Check your GitHub Vault.")
        return

    creds = Credentials(
        None, 
        refresh_token=token, 
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id, 
        client_secret=client_secret
    )
    
    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f"CBME Medical Series: {topic['title']}",
                "description": f"Institutional review of {topic['sub']}. PhD-level manuscript and quality support by KFC Lab.",
                "categoryId": "27",
                "tags": ["MBBS", "MLT", "CBME", "Medical Education", topic['tag']]
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("medical_cbme.mp4")
    )
    response = request.execute()
    print(f"✅ CBME Asset '{topic['title']}' Published! ID: {response.get('id')}")

if __name__ == "__main__":
    current_topic = get_random_cbme_topic()
    render_720p(current_topic)
    try:
        upload(current_topic)
    except Exception as e:
        print(f"⚠️ YouTube Factory Error: {e}")
