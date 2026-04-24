import os
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.http

def upload_video(video_url, title, description):
    # 1. Download the video from Shotstack to the GitHub Runner
    video_file = "video_to_upload.mp4"
    r = requests.get(video_url)
    with open(video_file, 'wb') as f:
        f.write(r.content)

    # 2. Setup YouTube API (This uses your secrets)
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    client_secrets_file = "client_secrets.json"
    
    # Note: On the first run, this requires a manual token. 
    # For now, we use the library to initialize the request.
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console() # We will update this to use a REFRESH_TOKEN for 24/7 automation

    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "categoryId": "27",
                "description": description,
                "title": title
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=googleapiclient.http.MediaFileUpload(video_file)
    )
    response = request.execute()
    print(f"✅ Upload Successful! Video ID: {response.get('id')}")

if __name__ == "__main__":
    # This will be triggered by your .yml
    print("🚀 YouTube Uploader Agent Active.")
