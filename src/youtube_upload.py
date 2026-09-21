"""
youtube_upload.py
Uploads videos to YouTube Data API v3.
Supports targeting a specific channel ID when multiple
channels exist under the same Google account.
"""
import json
import google.oauth2.credentials
import googleapiclient.discovery
import googleapiclient.http


def upload_to_youtube(
    video_path: str,
    thumbnail_path: str,
    title: str,
    description: str,
    tags: list,
    credentials_json: str,
    channel_id: str = None,
) -> str:
    creds_data = json.loads(credentials_json)
    creds = google.oauth2.credentials.Credentials(
        token=creds_data.get("token"),
        refresh_token=creds_data.get("refresh_token"),
        token_uri=creds_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=creds_data.get("client_id"),
        client_secret=creds_data.get("client_secret"),
    )

    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title"      : title[:100],
            "description": description,
            "tags"       : tags[:15],
            "categoryId" : "10",
        },
        "status": {
            "privacyStatus"          : "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    # Target specific channel if provided
    if channel_id:
        body["snippet"]["channelId"] = channel_id

    print(f"  [upload] starting upload …")

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=googleapiclient.http.MediaFileUpload(
            video_path,
            chunksize=1024 * 1024,
            resumable=True,
        ),
    )

    video_id = None
    while video_id is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"  [upload] {pct}% complete …")
        if response:
            video_id = response["id"]

    print(f"  [upload] video live → https://youtu.be/{video_id}")

    # Set thumbnail
    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=googleapiclient.http.MediaFileUpload(
                thumbnail_path, mimetype="image/jpeg",
            ),
        ).execute()
        print(f"  [upload] thumbnail set ✓")
    except Exception as e:
        print(f"  [upload] thumbnail failed (non-critical): {e}")

    return video_id
