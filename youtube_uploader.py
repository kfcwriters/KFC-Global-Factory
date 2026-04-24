import os, time, requests
import googleapiclient.discovery
import googleapiclient.http
from google_auth_oauthlib.flow import InstalledAppFlow

def upload_to_youtube():
    render_id = os.getenv('RENDER_ID')
    api_key = "ExZhq8U3rOIRgdUQDeIbar4vwtbM6GLAwn2Ei3Hq"
    
    # 1. Wait for render to finish
    for _ in range(10):
        time.sleep(30)
        res = requests.get(f"https://api.shotstack.io/edit/v1/render/{render_id}", headers={"x-api-key": api_key}).json()
        if res.get('response', {}).get('status') == 'completed':
            video_url = res['response']['url']
            break
    
    # 2. Download Video
    r = requests.get(video_url)
    with open("cbme_lesson.mp4", "wb") as f: f.write(r.content)

    # 3. Upload using your client_secrets.json
    # Note: On first run, it will print an Auth URL in the GitHub Logs.
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes)
    credentials = flow.run_local_server(port=0) # For GitHub, use run_console() if available
    
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    request = youtube.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": "CBME Medical Lesson", "categoryId": "27"}, "status": {"privacyStatus": "public"}},
        media_body=googleapiclient.http.MediaFileUpload("cbme_lesson.mp4")
    )
    request.execute()
    print("✅ YouTube Upload Complete!")

if __name__ == "__main__":
    upload_to_youtube()
