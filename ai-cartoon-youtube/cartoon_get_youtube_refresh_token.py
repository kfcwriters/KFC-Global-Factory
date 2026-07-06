"""
RUN THIS ONCE, ON YOUR OWN COMPUTER (not in GitHub Actions).

It opens a browser, you log into the YouTube channel's Google account,
approve access, and this prints a refresh_token you paste into
GitHub Secrets as YOUTUBE_REFRESH_TOKEN_CARTOON. You only ever do this once
(unless you revoke access).

Prereqs:
  1. Go to https://console.cloud.google.com/
  2. Create a project -> enable "YouTube Data API v3"
  3. Configure OAuth consent screen (External, add your own email as a test user)
  4. Create OAuth Client ID -> Application type: "Desktop app"
  5. Download the cartoon_client_secret.json and place it next to this script

Install: pip install google-auth-oauthlib
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "cartoon_client_secret.json")

if __name__ == "__main__":
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n\n=== SAVE THESE AS GITHUB SECRETS ===")
    print(f"YOUTUBE_CLIENT_ID_CARTOON={creds.client_id}")
    print(f"YOUTUBE_CLIENT_SECRET_CARTOON={creds.client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN_CARTOON={creds.refresh_token}")
    print("=====================================")
