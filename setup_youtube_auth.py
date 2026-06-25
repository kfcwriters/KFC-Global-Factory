#!/usr/bin/env python3
"""
setup_youtube_auth.py
======================
Run this ONCE on your local machine to generate the OAuth 2.0 credentials
that GitHub Actions will use to upload videos.

Steps:
  1.  Go to https://console.cloud.google.com/
  2.  Create a project (or select existing one)
  3.  Enable "YouTube Data API v3"  →  APIs & Services → Library
  4.  Create OAuth credentials      →  APIs & Services → Credentials
        Application type: Desktop app
        Download the JSON file → save as  client_secrets.json  in this folder
  5.  In OAuth consent screen:
        • Add your Google account as a "Test user"
        • Set Publishing status to "In production" (avoids 7-day token expiry)
  6.  Run:   python setup_youtube_auth.py
  7.  A browser tab will open — log in with your YouTube channel account
  8.  Copy the printed JSON block → paste into GitHub Secrets as YOUTUBE_CREDENTIALS

Requirements (install locally):
    pip install google-auth-oauthlib
"""

import json
import sys
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    sys.exit("Install dependency first:  pip install google-auth-oauthlib")


SECRETS_FILE = Path("client_secrets.json")
SCOPES       = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    if not SECRETS_FILE.exists():
        sys.exit(
            "❌  client_secrets.json not found.\n"
            "    Download it from Google Cloud Console → APIs & Services → Credentials"
        )

    print("🌐  Opening browser for Google OAuth login …")
    flow        = InstalledAppFlow.from_client_secrets_file(str(SECRETS_FILE), scopes=SCOPES)
    credentials = flow.run_local_server(port=8080, prompt="consent")

    creds_dict = {
        "token"        : credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri"    : credentials.token_uri,
        "client_id"    : credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes"       : list(credentials.scopes),
    }

    json_output = json.dumps(creds_dict, indent=2)

    print("\n" + "=" * 65)
    print("✅  SUCCESS — Copy the JSON below into GitHub Secrets")
    print("    Repo → Settings → Secrets and variables → Actions → New secret")
    print("    Secret name:  YOUTUBE_CREDENTIALS")
    print("=" * 65)
    print(json_output)
    print("=" * 65)

    # Also save locally for verification (NEVER commit this file)
    out = Path("youtube_credentials.json")
    out.write_text(json_output)
    print(f"\n💾  Also saved to {out} (add to .gitignore — do NOT commit!)")


if __name__ == "__main__":
    main()
