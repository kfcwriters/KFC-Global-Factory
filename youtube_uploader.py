import os, time, requests
import googleapiclient.discovery
import googleapiclient.http
from google_auth_oauthlib.flow import InstalledAppFlow

def upload_to_youtube():
    render_id = os.getenv('RENDER_ID')
    api_key = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq"
    video_url = None
    
    print(f"🛰️ Deep-Wait Mode Active (10 Minutes) for Render: {render_id}")

    for attempt in range(20):
        res = requests.get(f"https://api.shotstack.io/edit/v1/render/{render_id}", 
                           headers={"x-api-key": api_key}).json()
        status = res.get('response', {}).get('status', '').lower()
        print(f"📊 Attempt {attempt+1}/20: Status is '{status}'")
        
        if status in ['completed', 'done']:
            video_url = res['response'].get('url')
            if video_url:
                print(f"✅ Video is officially ready.")
                break
        time.sleep(30) 

    if not video_url:
        print("❌ Timeout reached.")
        return

    # 📥 Download
    r = requests.get(video_url)
    with open("cbme_lesson.mp4", "wb") as f: f.write(r.content)

    # 🚀 YouTube Push - FIXED COMMAND BELOW
    try:
        scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes)
        
        # FIX: Changed run_console() to run_local_server with console redirect
        # This will print the URL in your GitHub logs for you to click.
        credentials = flow.run_local_server(
            host='localhost',
            port=8080,
            authorization_prompt_message='Please visit this URL: {url}',
            success_message='The auth flow is complete; you may close this window.',
            open_browser=False
        )
        
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
        request = youtube.videos().insert(
            part="snippet,status",
            body={"snippet": {"title": "CBME Medical Lesson", "categoryId": "27"}, "status": {"privacyStatus": "public"}},
            media_body=googleapiclient.http.MediaFileUpload("cbme_lesson.mp4")
        )
        request.execute()
        print("🎉 SUCCESS! Video is live on YouTube.")
    except Exception as e:
        print(f"❌ YouTube API Error: {e}")

if __name__ == "__main__":
    upload_to_youtube()
