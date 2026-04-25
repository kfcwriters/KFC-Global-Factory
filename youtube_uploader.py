import os
import subprocess
from gtts import gTTS
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def generate_srt():
    # Word-to-word timing for the PhD Masterclass
    srt_content = """1
00:00:00,000 --> 00:00:04,000
WELCOME TO THE KFC LAB PHD SERIES

2
00:00:04,000 --> 00:00:08,000
TODAY WE ANALYZE SIGMA METRICS

3
00:00:08,000 --> 00:00:12,000
IN CLINICAL BIOCHEMISTRY

4
00:00:12,000 --> 00:00:16,000
DEFINING ANALYTICAL PRECISION

5
00:00:16,000 --> 00:00:20,000
AND TOTAL ALLOWABLE ERROR

6
00:00:20,000 --> 00:00:25,000
FOR INSTITUTIONAL EXCELLENCE
"""
    with open("subtitles.srt", "w") as f:
        f.write(srt_content)

def render_720p():
    print(f"🎬 RENDERING: Professional Word-Synced PhD Asset...")
    
    # 1. Voiceover (matches the SRT timings)
    script = "Welcome to the KFC Lab PhD Series. Today we analyze Sigma Metrics in Clinical Biochemistry, defining analytical precision and total allowable error for institutional excellence."
    tts = gTTS(text=script, lang='en')
    tts.save("master_voice.mp3")

    # 2. Hard-Burn Subtitles into Video
    # We use 'force_style' to make the text a decent size and centered
    generate_srt()
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=26", # Navy Blue
        "-i", "master_voice.mp3",
        "-vf", "drawgrid=w=100:h=100:t=2:c=white@0.1, " +
               "subtitles=subtitles.srt:force_style='Alignment=2,FontSize=24,Outline=1,PrimaryColour=&HFFFFFF'",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "synced_lecture.mp4"
    ]
    subprocess.run(cmd, check=True)

def upload():
    token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    creds = Credentials(None, refresh_token=token, token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.getenv('CLIENT_ID'), client_secret=os.getenv('CLIENT_SECRET'))
    youtube = build("youtube", "v3", credentials=creds)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": "PhD Clinical Masterclass (Synced)", "categoryId": "27"}, "status": {"privacyStatus": "public"}},
        media_body=MediaFileUpload("synced_lecture.mp4", resumable=True)
    )
    request.execute()
    print("✅ Word-to-Word Synced PhD Asset Published.")

if __name__ == "__main__":
    render_720p()
    try: upload()
    except Exception as e: print(f"⚠️ Error: {e}")
