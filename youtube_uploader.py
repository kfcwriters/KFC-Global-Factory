import os
import time
import requests
import googleapiclient.discovery
import googleapiclient.http
from google_auth_oauthlib.flow import InstalledAppFlow

def upload_to_youtube():
    render_id = os.getenv('RENDER_ID')
    api_key = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq"
    video_url = None
    
    print(f"🛰️ Starting YouTube Uploader for Render: {render_id}")

    # 🕒 1. Patient Polling Loop
    for attempt in range(10):
        print(f"Attempt {attempt+1}: Checking Shotstack status...")
        res = requests.get(f"https://api.shotstack.io/edit/v1/render/{render_id}", 
                           headers={"x-api-key": api_key}).json()
        
        status = res.get('response', {}).get('status')
        print(f"📊 Status: {status}")
        
        if status == 'completed':
            video_url = res['response']['url']
            print(f"✅ Video is ready at: {video_url}")
            break
        elif status == 'failed':
            print("❌ Render failed on Shotstack.")
            return
        
        time.sleep(30) # Wait 30 seconds before next check

    if not video_url:
        print("⚠️ Timeout: Video not ready after 5 minutes.")
        return

    # 📥 2. Download the Video
    print("📥 Downloading video...")
    r = requests.get(video_url)
    with open("cbme_lesson.mp4", "wb") as f:
        f.write(r.content)

    # 🚀 3. YouTube Upload Logic
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    # Ensure client_secrets.json is in your repo!
    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes)
    
    # Note: For GitHub Actions, this will prompt for a code in the logs.
    credentials = flow.run_local_server(port=0, open_browser=False)
    
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f"CBME Medical Lesson #{os.getenv('RANDOM', '1')}",
                "description": "High-yield Biochemistry for MBBS/MLT. Powered by KFC Lab.",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=googleapiclient.http.MediaFileUpload("cbme_lesson.mp4")
    )
    
    print("📤 Pushing to YouTube...")
    response = request.execute()
    print(f"🎉 SUCCESS! Video ID: {response.get('id')}")

if __name__ == "__main__":
    upload_to_youtube()
