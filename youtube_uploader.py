import os
import subprocess
import googleapiclient.discovery
import googleapiclient.http
from google_auth_oauthlib.flow import InstalledAppFlow

def create_and_upload():
    # 🎙️ High-Yield Topic: HbA1c Clinical Significance
    topic = "Clinical Significance of HbA1c"
    script = "HbA1c monitoring is the gold standard for long-term glycemic control. A level below seven percent is generally targeted to prevent diabetic complications."
    
    print(f"🎬 Initializing Arcreel Engine for: {topic}")
    
    # 🛠️ Step 1: Create Video (with detailed error logs)
    try:
        # Check if ffmpeg is available
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        print("✅ System Video Engine Verified.")
        
        # Run Arcreel
        subprocess.run([
            "arcreel", "create", 
            "--topic", topic, 
            "--script", script, 
            "--output", "cbme_lesson.mp4"
        ], check=True)
        print("✅ Arcreel Render Successful.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Arcreel Command Failed with exit code {e.returncode}")
        return
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        return

    # 🚀 Step 2: YouTube Upload
    video_file = "cbme_lesson.mp4"
    if not os.path.exists(video_file):
        print("❌ Video File Missing. Aborting upload.")
        return

    try:
        scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", scopes)
        
        credentials = flow.run_local_server(
            host='localhost', port=8080, 
            authorization_prompt_message='Please visit: {url}', 
            open_browser=False
        )
        
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {"title": f"CBME Medical: {topic}", "description": "PhD-level clinical education.", "categoryId": "27"},
                "status": {"privacyStatus": "public"}
            },
            media_body=googleapiclient.http.MediaFileUpload(video_file)
        )
        request.execute()
        print("🎉 SUCCESS! Video Live on Channel.")
    except Exception as e:
        print(f"❌ YouTube API Failure: {e}")

if __name__ == "__main__":
    create_and_upload()
