import os
import googleapiclient.discovery
import googleapiclient.http
from google_auth_oauthlib.flow import InstalledAppFlow

def upload_to_youtube():
    # 📁 Step 1: Check if Arcreel finished the video
    video_file = "cbme_lesson.mp4"
    if not os.path.exists(video_file):
        print("❌ Error: Video file not found. Arcreel step failed.")
        return

    print(f"✅ Video found. Preparing YouTube upload for Clinical Biochemistry...")

    # 🚀 Step 2: YouTube API Authorization
    try:
        scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes)
        
        # This URL will appear in your GitHub Action logs
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
                    "title": "CBME Medical Lesson: High-Yield Biochemistry",
                    "description": "Daily clinical education powered by KFC Lab.",
                    "categoryId": "27"
                },
                "status": {"privacyStatus": "public"}
            },
            media_body=googleapiclient.http.MediaFileUpload(video_file)
        )
        
        print("📤 Pushing to YouTube...")
        response = request.execute()
        print(f"🎉 SUCCESS! Video Live: https://www.youtube.com/watch?v={response.get('id')}")
        
    except Exception as e:
        print(f"❌ YouTube API Error: {e}")

if __name__ == "__main__":
    upload_to_youtube()
