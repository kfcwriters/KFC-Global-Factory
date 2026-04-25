import os
import subprocess
import googleapiclient.discovery
import googleapiclient.http
from google_auth_oauthlib.flow import InstalledAppFlow

def create_and_upload():
    # 🎙️ Clinical Script Generation
    topic = "Clinical Significance of Glycated Hemoglobin (HbA1c)"
    script = "HbA1c reflects average plasma glucose over eight to twelve weeks. It is a gold standard for monitoring long-term glycemic control in diabetes mellitus."
    
    print(f"🎬 Arcreel is generating medical video: {topic}")
    
    # 🛠️ Step 1: Run Arcreel via Command Line
    # This creates 'output.mp4' on the server
    try:
        subprocess.run([
            "arcreel", "create", 
            "--topic", topic, 
            "--script", script, 
            "--style", "medical", 
            "--output", "cbme_lesson.mp4"
        ], check=True)
    except Exception as e:
        print(f"❌ Arcreel Generation Failed: {e}")
        return

    # 🚀 Step 2: YouTube Upload Logic
    video_file = "cbme_lesson.mp4"
    if not os.path.exists(video_file):
        print("❌ Error: Video file was not created.")
        return

    try:
        scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes)
        
        # Link appears in GitHub Logs
        credentials = flow.run_local_server(
            host='localhost', port=8080, 
            authorization_prompt_message='Please visit: {url}', 
            open_browser=False
        )
        
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {"title": f"CBME Lesson: {topic}", "description": "High-yield medical education.", "categoryId": "27"},
                "status": {"privacyStatus": "public"}
            },
            media_body=googleapiclient.http.MediaFileUpload(video_file)
        )
        request.execute()
        print("🎉 SUCCESS! Video is live.")
    except Exception as e:
        print(f"❌ YouTube Error: {e}")

if __name__ == "__main__":
    create_and_upload()
