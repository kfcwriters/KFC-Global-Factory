import os
import time
import requests
import googleapiclient.discovery
import googleapiclient.http
from google_auth_oauthlib.flow import InstalledAppFlow

def upload_to_youtube():
    # 💾 1. Physical Handshake: Read the ID saved by the .yml
    try:
        if not os.path.exists("render_id.txt"):
            print("❌ Error: render_id.txt not found. Step 2 must have failed.")
            return
            
        with open("render_id.txt", "r") as f:
            render_id = f.read().strip()
        
        if render_id == "failed" or not render_id or render_id == "null":
            print(f"❌ Uploader Aborted: Invalid Render ID found ({render_id}).")
            return
    except Exception as e:
        print(f"❌ Critical error reading handshake file: {e}")
        return

    api_key = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq"
    video_url = None
    
    print(f"🛰️ Deep-Wait Mode Active for Render: {render_id}")

    # 🕒 2. The 10-Minute Patient Polling Loop (20 attempts x 30s)
    for attempt in range(20):
        try:
            res = requests.get(f"https://api.shotstack.io/edit/v1/render/{render_id}", 
                               headers={"x-api-key": api_key}).json()
            
            # Extract status safely
            status = res.get('response', {}).get('status', '').lower()
            print(f"📊 Attempt {attempt+1}/20: Status is '{status}'")
            
            if status in ['completed', 'done']:
                video_url = res['response'].get('url')
                if video_url:
                    print(f"✅ Lesson Ready for Download: {video_url}")
                    break
            elif status == 'failed':
                print("❌ Shotstack Server Error: Render failed internally.")
                return
        except Exception as e:
            print(f"⚠️ Connection glitch (retrying...): {e}")
        
        time.sleep(30) 

    if not video_url:
        print("❌ Final Timeout: Video not ready after 10 minutes. Shotstack is overwhelmed.")
        return

    # 📥 3. Download the teaching video to the GitHub Runner
    print("📥 Downloading CBME Lesson file...")
    r = requests.get(video_url)
    with open("cbme_lesson.mp4", "wb") as f:
        f.write(r.content)

    # 🚀 4. YouTube API Authorization and Upload
    try:
        scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        # Ensure client_secrets.json is in your GitHub main folder!
        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes)
        
        # This prints the URL in your GitHub logs. You must click and authorize.
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
                    "title": "CBME Clinical Biochemistry Lesson",
                    "description": "High-yield medical education for students. Produced by KFC Lab.",
                    "categoryId": "27", # Education Category
                    "tags": ["Biochemistry", "MBBS", "CBME", "Medical Education"]
                },
                "status": {"privacyStatus": "public"}
            },
            media_body=googleapiclient.http.MediaFileUpload("cbme_lesson.mp4")
        )
        
        print("📤 Pushing video to YouTube channel...")
        response = request.execute()
        print(f"🎉 SUCCESS! Lesson Live at: https://www.youtube.com/watch?v={response.get('id')}")
        
    except Exception as e:
        print(f"❌ YouTube API Error: {e}")

if __name__ == "__main__":
    upload_to_youtube()
