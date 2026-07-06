"""
RUN THIS ONCE, LOCALLY (not in GitHub Actions).

Prereqs:
  1. https://console.cloud.google.com/ -> new project
  2. Enable "YouTube Data API v3"
  3. OAuth consent screen -> External -> add your email as test user
     -> Publishing status: "In production" (avoids 7-day token expiry)
  4. Credentials -> Create Credentials -> OAuth client ID -> Desktop app
  5. Download JSON, save as client_secrets.json next to this script

Install: pip install google-auth-oauthlib
Run:     python setup_youtube_auth.py
"""
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secrets.json"

if __name__ == "__main__":
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    creds_dict = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": SCOPES,
    }

    print("\n\n=== COPY THIS ENTIRE JSON BLOCK ===")
    print(json.dumps(creds_dict))
    print("=== Paste it as the GitHub secret: YOUTUBE_CREDENTIALS_MUSIC ===")
