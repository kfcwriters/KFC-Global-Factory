"""
Step 5: Upload the finished video to YouTube.

This uses a one-time OAuth refresh token (generated locally via
get_youtube_refresh_token.py) so the GitHub Actions runner can upload
without any interactive browser login.

Required environment variables (set as GitHub Secrets):
  YOUTUBE_CLIENT_ID_CARTOON
  YOUTUBE_CLIENT_SECRET_CARTOON
  YOUTUBE_REFRESH_TOKEN_CARTOON

Install: pip install google-auth google-auth-oauthlib google-api-python-client
"""
import os
import sys
import json
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "config"))
from cartoon_config import CHANNEL_NAME, YOUTUBE_CATEGORY_ID, YOUTUBE_PRIVACY, MADE_FOR_KIDS


def get_authenticated_service():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN_CARTOON"],
        client_id=os.environ["YOUTUBE_CLIENT_ID_CARTOON"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET_CARTOON"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    creds.refresh(google.auth.transport.requests.Request())
    return build("youtube", "v3", credentials=creds)


def upload_video(video_path: str, title: str, description: str, tags: list):
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": YOUTUBE_CATEGORY_ID,
        },
        "status": {
            "privacyStatus": YOUTUBE_PRIVACY,
            "selfDeclaredMadeForKids": MADE_FOR_KIDS,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print("Uploading...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}% uploaded")

    video_id = response["id"]
    print(f"Upload complete: https://youtube.com/watch?v={video_id}")
    return video_id


if __name__ == "__main__":
    base = os.path.join(os.path.dirname(__file__), "..", "cartoon_output")
    with open(os.path.join(base, "script.json")) as f:
        scenes = json.load(f)

    topic = sys.argv[1] if len(sys.argv) > 1 else "Episode"
    title = f"{topic.title()} | {CHANNEL_NAME}"
    description = (
        f"A gentle story for kids: {topic}\n\n"
        f"Subscribe to {CHANNEL_NAME} for more stories!\n\n"
        "This video was created with AI-assisted narration and illustration."
    )
    upload_video(
        video_path=os.path.join(base, "final_episode.mp4"),
        title=title,
        description=description,
        tags=["kids cartoon", "children's story", "bedtime story", CHANNEL_NAME],
    )
