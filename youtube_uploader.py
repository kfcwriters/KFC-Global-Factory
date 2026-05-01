import os
import requests
import json

def upload_to_youtube():
    video_path = 'final_module.mp4'
    if not os.path.exists(video_path):
        print("❌ No video file found to upload.")
        return

    # 1. Get Access Token using your Refresh Token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'refresh_token': os.getenv('YOUTUBE_REFRESH_TOKEN'),
        'grant_type': 'refresh_token'
    }
    
    r = requests.post(token_url, data=token_data)
    access_token = r.json().get('access_token')

    # 2. Upload Metadata and Video
    url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status"
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Professional Medical Metadata
    metadata = {
        "snippet": {
            "title": "Global Medical Science Masterclass 2026",
            "description": "Manual expert analysis of cutting-edge clinical research. #Medicine #PhD #Science",
            "categoryId": "27" # Education
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    files = {
        'json': (None, json.dumps(metadata), 'application/json'),
        'video': (video_path, open(video_path, 'rb'), 'application/octet-stream')
    }

    response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        print("🚀 SUCCESS: Video uploaded to YouTube.")
    else:
        print(f"❌ Upload Failed: {response.text}")

if __name__ == "__main__":
    upload_to_youtube()
