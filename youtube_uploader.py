import os
import time
import requests
import googleapiclient.discovery
import googleapiclient.http
from google_auth_oauthlib.flow import InstalledAppFlow

def upload_to_youtube():
    # 💾 Step 1: Read the RENDER_ID from the physical file
    try:
        with open("render_id.txt", "r") as f:
            render_id = f.read().strip()
        if not render_id or render_id == "null":
            raise ValueError("Render ID in file is empty or null.")
    except Exception as e:
        print(f"❌ Error reading render_id.txt: {e}")
        return

    api_key = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq"
    video_url = None
    
    print(f"🛰️ Deep-Wait Mode Active for Render: {render_id}")

    # 🕒 Step 2: The 10-Minute Polling Loop (20 attempts x 30s)
    for attempt in range(20):
        try:
            res = requests.get(f"https://api.shotstack.io/edit/v1/render/{render_id}", 
                               headers={"x-api-key": api_key}).json()
            
            status = res.get('response', {}).get('status', '').lower()
            print(f"📊 Attempt {attempt+1}/20: Status is '{status}'")
            
            if status in ['completed', 'done']:
                video_url = res['response'].get('url')
                if video_url:
                    print(f"✅ Video is Ready: {video_url}")
                    break
            elif status == 'failed':
                print("❌ Render failed on Shotstack servers.")
                return
        except Exception as e:
            print(f"⚠️ Connection glitch: {e}")
        
        time.sleep(30) 

    if not video_url:
        print("❌ Final Timeout: Video not ready after 10 minutes.")
        return

    # 📥 Step 3: Download the teaching video
    print("📥 Downloading CBME Lesson...")
    r = requests.get(video_url)
    with open("cbme_lesson.mp4", "wb") as f:
        f.write(r.content)

    # 🚀 Step 4: YouTube Upload
    try:
        scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes)
        
        # This will print the URL in GitHub logs for you to authorize
        credentials = flow.run_local_server(
            host='localhost',
            port=8080,
            authorization_prompt_message='Please visit this URL: {url}',
            open_browser=False
        )
        
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
        
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": "CBME Medical Biochemistry High-Yield Lesson",
                    "description": "Daily clinical education powered by KFC Lab.",
                    "categoryId": "27"
                },
                "status": {"privacyStatus": "public"}
            },
            media_body=googleapiclient.http.MediaFileUpload("cbme_lesson.mp4")
        )
        
        print("📤 Pushing to YouTube channel...")
        response = request.execute()
        print(f"🎉 SUCCESS! Video ID: {response.get('id')}")
    except Exception as e:
        print(f"❌ YouTube API Error: {e}")

if __name__ == "__main__":
    upload_to_youtube()
