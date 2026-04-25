import os
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def render_720p():
    print("🎬 Rendering 720p Clinical Asset...")
    text = "HbA1c Significance\nAnalytical Quality Management"
    cmd = (
        f'ffmpeg -y -f lavfi -i color=c=0x000032:s=1280x720:d=5 '
        f'-vf "drawtext=text=\'{text}\':fontcolor=white:fontsize=45:x=(w-text_w)/2:y=(h-text_h)/2" '
        f'-c:v libx264 -pix_fmt yuv420p video.mp4'
    )
    subprocess.run(cmd, shell=True, check=True)

def upload():
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
        body={"snippet": {"title": "HbA1c Lab Quality", "categoryId": "27"}, "status": {"privacyStatus": "public"}},
        media_body=MediaFileUpload("video.mp4")
    )
    request.execute()
    print("✅ Video Uploaded successfully.")

if __name__ == "__main__":
    render_720p()
    try: upload()
    except Exception as e: print(f"⚠️ YouTube Error: {e}")
