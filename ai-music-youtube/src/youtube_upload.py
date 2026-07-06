"""
Uploads the finished video + thumbnail to YouTube.

Reads the full OAuth credentials JSON blob from the
YOUTUBE_CREDENTIALS_MUSIC env var (generated once locally via
ai_music_setup_youtube_auth.py). Named distinctly so it can't collide
with a credentials secret used by any other project in the same repo.
"""
import os
import json
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def get_authenticated_service():
    creds_json = json.loads(os.environ["YOUTUBE_CREDENTIALS_MUSIC"])
    creds = Credentials(
        token=creds_json.get("token"),
        refresh_token=creds_json["refresh_token"],
        client_id=creds_json["client_id"],
        client_secret=creds_json["client_secret"],
        token_uri=creds_json.get("token_uri", "https://oauth2.googleapis.com/token"),
        scopes=creds_json.get("scopes", ["https://www.googleapis.com/auth/youtube.upload"]),
    )
    creds.refresh(google.auth.transport.requests.Request())
    return build("youtube", "v3", credentials=creds)


def upload_video(video_path: str, title: str, description: str, tags: list,
                  thumbnail_path: str = None, privacy: str = "public", made_for_kids: bool = False):
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "10",  # Music
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print("Uploading video...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}% uploaded")

    video_id = response["id"]
    print(f"Upload complete: https://youtube.com/watch?v={video_id}")

    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id, media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("Custom thumbnail set.")
        except Exception as e:
            # Requires a phone-verified YouTube account; fails silently otherwise.
            print(f"  Could not set thumbnail (account may need phone verification): {e}")

    return video_id
