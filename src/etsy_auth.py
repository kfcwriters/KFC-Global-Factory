"""
etsy_auth.py
One-time OAuth token generator for Etsy API v3.
Run this ONCE locally on your computer to get an access token + refresh token.
The refresh token lasts much longer and can be used to auto-refresh the access token.
"""
import hashlib, base64, os, secrets, requests, json, webbrowser
from urllib.parse import urlencode, urlparse, parse_qs


def get_oauth_tokens(api_key: str, shared_secret: str) -> dict:
    """
    Complete OAuth 2.0 PKCE flow for Etsy API v3.
    Returns dict with access_token and refresh_token.
    """
    # Step 1: Generate PKCE code verifier and challenge
    code_verifier = secrets.token_urlsafe(64)[:128]
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode()

    state = secrets.token_urlsafe(16)

    # Scopes needed for creating listings and uploading files
    scopes = [
        "listings_r", "listings_w",
        "listings_d",
        "shops_r", "shops_w",
    ]

    # Step 2: Build authorization URL
    params = {
        "response_type"         : "code",
        "client_id"             : api_key,
        "redirect_uri"          : "https://www.example.com/callback",
        "scope"                 : " ".join(scopes),
        "state"                 : state,
        "code_challenge"        : code_challenge,
        "code_challenge_method" : "S256",
    }

    auth_url = "https://www.etsy.com/oauth/connect?" + urlencode(params)

    print("\n" + "="*60)
    print("ETSY OAUTH SETUP — One-time process")
    print("="*60)
    print("\n1. Open this URL in your browser:")
    print(f"\n{auth_url}\n")
    print("2. Log into Etsy and click 'Allow Access'")
    print("3. You'll be redirected to example.com (which won't load — that's OK)")
    print("4. Copy the FULL URL from your browser's address bar")
    print("   It will look like: https://www.example.com/callback?code=xxx&state=yyy")
    print("\n" + "="*60)

    callback_url = input("\nPaste the full callback URL here: ").strip()

    # Step 3: Extract authorization code from callback URL
    parsed = urlparse(callback_url)
    query_params = parse_qs(parsed.query)

    if "code" not in query_params:
        raise ValueError(f"No 'code' found in URL: {callback_url}")

    auth_code = query_params["code"][0]
    returned_state = query_params.get("state", [""])[0]

    if returned_state != state:
        print(f"Warning: State mismatch. Expected {state}, got {returned_state}")

    print(f"\nAuthorization code received ✓")

    # Step 4: Exchange code for tokens
    token_resp = requests.post(
        "https://openapi.etsy.com/v3/public/oauth/token",
        data={
            "grant_type"    : "authorization_code",
            "client_id"     : api_key,
            "redirect_uri"  : "https://www.example.com/callback",
            "code"          : auth_code,
            "code_verifier" : code_verifier,
        },
        timeout=30
    )

    if not token_resp.ok:
        raise RuntimeError(f"Token exchange failed: {token_resp.status_code} {token_resp.text}")

    tokens = token_resp.json()
    print(f"\n✅ OAuth tokens obtained!")
    print(f"\nACCESS TOKEN (expires in 1 hour):")
    print(f"  {tokens['access_token'][:40]}...")
    print(f"\nREFRESH TOKEN (use to get new access tokens):")
    print(f"  {tokens['refresh_token'][:40]}...")

    return tokens


def refresh_access_token(api_key: str, refresh_token: str) -> str:
    """
    Use the refresh token to get a new access token.
    Call this before each GitHub Actions run to get a fresh token.
    """
    resp = requests.post(
        "https://openapi.etsy.com/v3/public/oauth/token",
        data={
            "grant_type"    : "refresh_token",
            "client_id"     : api_key,
            "refresh_token" : refresh_token,
        },
        timeout=30
    )

    if not resp.ok:
        raise RuntimeError(f"Token refresh failed: {resp.status_code} {resp.text}")

    new_access_token = resp.json()["access_token"]
    print(f"  [etsy-auth] Access token refreshed ✓")
    return new_access_token


if __name__ == "__main__":
    print("Etsy OAuth Token Generator")
    api_key       = input("Enter your Etsy API keystring: ").strip()
    shared_secret = input("Enter your Etsy shared secret: ").strip()
    tokens        = get_oauth_tokens(api_key, shared_secret)

    print("\n" + "="*60)
    print("ADD THESE AS GITHUB SECRETS:")
    print("="*60)
    print(f"\nETSY_API_KEY     = {api_key}")
    print(f"ETSY_REFRESH_TOKEN = {tokens['refresh_token']}")
    print("\nThe pipeline will auto-refresh the access token each run.")
    print("The refresh token is long-lived (90 days).")
    print("="*60)
