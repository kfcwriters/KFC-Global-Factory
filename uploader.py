import os
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_service():
    creds = google.oauth2.credentials.Credentials(
        None,
        refresh_token=os.environ.get('NEW_YT_REFRESH_TOKEN'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get('NEW_YT_CLIENT_ID'),
        client_secret=os.environ.get('NEW_YT_CLIENT_SECRET')
    )
    return build('youtube', 'v3', credentials=creds)

def upload_video():
    youtube = get_service()
    
    # Path updated for 720p30 output folder created by -qm flag
    video_path = "media/videos/music_gen/720p30/NeonLyrics.mp4"
    
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        # List files to help debug if it fails again
        print("Existing files in media directory:")
        for root, dirs, files in os.walk("media"):
            print(f"Directory: {root}, Files: {files}")
        return

    body = {
        'snippet': {
            'title': 'Soulful AI Melodies #Shorts #Romantic',
            'description': 'Automated AI Romantic Vibes.',
            'tags': ['Romantic', 'AISongs', 'Shorts'],
            'categoryId': '10'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }

    print("Starting upload...")
    insert_request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )
    
    response = insert_request.execute()
    print(f"Success! Video ID: {response['id']}")

if __name__ == "__main__":
    upload_video()
