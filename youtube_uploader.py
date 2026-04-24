import os, time, requests
import googleapiclient.discovery
import googleapiclient.http
from google_auth_oauthlib.flow import InstalledAppFlow

def upload_to_youtube():
    render_id = os.getenv('RENDER_ID')
    api_key = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq"
    video_url = None
    
    print(f"🛰️ Deep-Wait Mode Active (10 Minutes) for Render: {render_id}")

    # 🕒 20 attempts x 30 seconds = 10 Minutes
    for attempt in range(20):
        res = requests.get(f"https://api.shotstack.io/edit/v1/render/{render_id}", 
                           headers={"x-api-key": api_key}).json()
        
        status = res.get('response', {}).get('status', '').lower()
        print(f"📊 Attempt {attempt+1}/20: Status is '{status}'")
        
        if status in ['completed', 'done']:
            video_url = res['response'].get('url')
            if video_url:
                print(f"✅ Lesson Ready: {video_url}")
                break
        time.sleep(30) 

    if not video_url:
        print("❌ Final Timeout: Video still processing after 10 minutes.")
        return

    # 📥 Download and 🚀 Upload logic below
    r = requests.get(video_url)
    with open("cbme_lesson.mp4", "wb") as f: f.write(r.content)

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes)
    credentials = flow.run_console() # Paste the code in GitHub Logs
    
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    request = youtube.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": "CBME Medical Lesson", "categoryId": "27"}, "status": {"privacyStatus": "public"}},
        media_body=googleapiclient.http.MediaFileUpload("cbme_lesson.mp4")
    )
    request.execute()
    print("🎉 SUCCESS! Video is live on YouTube.")

if __name__ == "__main__":
    upload_to_youtube()
