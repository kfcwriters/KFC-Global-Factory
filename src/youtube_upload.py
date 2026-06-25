"""
youtube_upload.py
Uploads a video + thumbnail to YouTube using OAuth 2.0 credentials
stored as a JSON string in the YOUTUBE_CREDENTIALS environment variable.
"""

import json

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def upload_to_youtube(
    video_path    : str,
    thumbnail_path: str,
    title         : str,
    description   : str,
    tags          : list[str],
    credentials_json: str,
) -> str:
    """
    Upload video to YouTube and optionally set its thumbnail.

    Args:
        video_path       : Path to the .mp4 file.
        thumbnail_path   : Path to the .jpg thumbnail.
        title            : Video title (≤100 chars).
        description      : Video description (≤5000 chars).
        tags             : List of tag strings.
        credentials_json : JSON string with OAuth2 token fields
                           (token, refresh_token, client_id, client_secret, token_uri).

    Returns:
        YouTube video ID string.
    """
    creds = _load_credentials(credentials_json)

    # Refresh access token if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    youtube = build("youtube", "v3", credentials=creds)

    # ── Video upload ─────────────────────────────────────────────────────────
    body = {
        "snippet": {
            "title"          : title[:100],
            "description"    : description[:5000],
            "tags"           : [t.lstrip("#") for t in tags][:500],
            "categoryId"     : "10",        # Music
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus"            : "public",
            "selfDeclaredMadeForKids"  : False,
            "madeForKids"              : False,
        },
    }

    media = MediaFileUpload(
        video_path,
        mimetype   = "video/mp4",
        resumable  = True,
        chunksize  = 5 * 1024 * 1024,   # 5 MB chunks
    )

    request  = youtube.videos().insert(
        part       = ",".join(body.keys()),
        body       = body,
        media_body = media,
    )

    print("  [upload] starting upload …")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"  [upload] {pct}% complete …")

    video_id = response["id"]
    print(f"  [upload] video live → https://youtu.be/{video_id}")

    # ── Thumbnail ────────────────────────────────────────────────────────────
    try:
        youtube.thumbnails().set(
            videoId    = video_id,
            media_body = MediaFileUpload(thumbnail_path, mimetype="image/jpeg"),
        ).execute()
        print("  [upload] thumbnail set ✓")
    except Exception as exc:
        # Thumbnail upload can fail if the channel isn't verified — non-fatal
        print(f"  [upload] thumbnail skipped ({exc})")

    return video_id


# ─────────────────────────────────────────
# Credential helpers
# ─────────────────────────────────────────

def _load_credentials(json_str: str) -> Credentials:
    """Parse YOUTUBE_CREDENTIALS JSON string into a Credentials object."""
    data = json.loads(json_str)
    return Credentials(
        token         = data.get("token"),
        refresh_token = data.get("refresh_token"),
        token_uri     = data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id     = data.get("client_id"),
        client_secret = data.get("client_secret"),
        scopes        = SCOPES,
    )
