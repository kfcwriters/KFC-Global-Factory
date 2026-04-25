import os
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def render_720p():
    print("🎬 FFmpeg: Rendering Global Medical Science Asset...")
    # Broader topic to attract all medical professionals
    text = "Precision Medicine: The Future of Surgery & Diagnostics\nPhD-Level Analytical Support"
    cmd = (
        f'ffmpeg -y -f lavfi -i color=c=0x000032:s=1280x720:d=5 '
        f'-vf "drawtext=text=\'{text}\':fontcolor=white:fontsize=35:x=(w-text_w)/2:y=(h-text_h)/2" '
        f'-c:v libx264 -pix_fmt yuv420p medical_science_720p.mp4'
    )
    subprocess.run(cmd, shell=True, check=True)

def upload():
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    if not token:
        print("⚠️ Waiting for YOUTUBE_REFRESH_TOKEN in GitHub Secrets...")
        return

    creds = Credentials(
        None,
        refresh_token=token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET')
    )
    
    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "Precision Medicine & Clinical Analytics",
                "description": "Institutional overview of advanced diagnostics and PhD-level research support.",
                "categoryId": "27",
                "tags": ["Medical Science", "Pathology", "Surgery", "Clinical Research"]
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("medical_science_720p.mp4")
    )
    request.execute()
    print("✅ Broad-Spectrum Medical Asset Published!")

if __name__ == "__main__":
    render_720p()
    upload()
