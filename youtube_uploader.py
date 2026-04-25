import os
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def create_720p_video():
    print("🎬 Rendering 720p Clinical Asset...")
    text = "HbA1c: Analytical Quality\nSigma Metrics in Lab Management"
    cmd = (
        f'ffmpeg -y -f lavfi -i color=c=0x000032:s=1280x720:d=5 '
        f'-vf "drawtext=text=\'{text}\':fontcolor=white:fontsize=45:x=(w-text_w)/2:y=(h-text_h)/2" '
        f'-c:v libx264 -pix_fmt yuv420p video_asset.mp4'
    )
    subprocess.run(cmd, shell=True, check=True)

def upload_to_youtube():
    creds = Credentials(
        None,
        refresh_token=os.getenv('YOUTUBE_REFRESH_TOKEN'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv('CLIENT_ID'),
        client_secret=os.getenv('CLIENT_SECRET')
    )
    
    youtube = build("youtube", "v3", credentials=creds)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "Clinical Significance of HbA1c",
                "description": "Educational short for MBBS/MLT students regarding Sigma metrics.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("video_asset.mp4")
    )
    response = request.execute()
    print(f"✅ Asset Published! Video ID: {response.get('id')}")

if __name__ == "__main__":
    create_720p_video()
    try:
        upload_to_youtube()
    except Exception as e:
        print(f"⚠️ YouTube Error: {e}")
