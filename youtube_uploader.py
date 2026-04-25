import os
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def render_720p():
    print("🎬 FFmpeg: Generating Industrial Test Asset (30s)...")
    
    # - testsrc: Generates a moving clock and color bars (Guaranteed visuals)
    # - aevalsrc: Generates white noise (Guaranteed audio)
    # This bypasses the 'font' errors entirely.
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc=size=1280x720:rate=25:d=30",
        "-f", "lavfi", "-i", "aevalsrc=-2+random(0):d=30",
        "-c:v", "libx264", "-pix_fmt", yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "industrial_output.mp4"
    ]
    subprocess.run(cmd, check=True)

def upload():
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
    
    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "Medical Science Series: Institutional Broadcast",
                "description": "24/7 Clinical Analytics & PhD Manuscript Support by KFC Lab.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload("industrial_output.mp4")
    )
    request.execute()
    print("✅ Industrial Asset Published Successfully.")

if __name__ == "__main__":
    render_720p()
    try: upload()
    except Exception as e: print(f"⚠️ Factory Error: {e}")
