"""
suno_gen.py
Automatically generates songs using Suno AI's internal API.
Requires SUNO_COOKIE secret (your browser session cookie).
Falls back to songs/ folder if cookie not set or generation fails.
"""
import time, random, requests

CLERK_URL = "https://clerk.suno.com/v1/client"
SUNO_API  = "https://studio-api.suno.ai/api"

ROMANTIC_PROMPTS = [
    "romantic love ballad, soft piano and violin, emotional female vocals, slow tempo, heartfelt",
    "beautiful romantic english love song, acoustic guitar, soulful female singer, slow ballad",
    "emotional love song, orchestra and piano, powerful female vocals, romantic, cinematic",
    "slow romantic love song, tender female voice, soft strings, heartfelt lyrics about love",
    "romantic bollywood inspired english love song, sitar and piano, soulful emotional ballad",
    "sweet love song, gentle acoustic guitar, warm female voice, romantic evening ballad",
    "powerful love ballad, piano and cello, emotional female singer, romantic and heartfelt",
    "romantic duet love song, male and female vocals, piano strings, slow emotional ballad",
]


def _parse_cookie(raw: str) -> str:
    """
    Converts cookie to simple key=value; key=value string.
    Handles EditThisCookie JSON: [{"name":"x","value":"y",...}]
    AND plain string: key=value; key=value
    """
    raw = raw.strip()
    if raw.startswith("["):
        import json
        items = json.loads(raw)
        parts = [f"{c['name']}={c['value']}" for c in items
                 if c.get("name") and c.get("value")]
        return "; ".join(parts)
    # Plain string — collapse any newlines/whitespace
    return " ".join(raw.split())


def _get_jwt(cookie: str) -> str:
    """Exchange Suno session cookie for a fresh JWT token."""
    cookie = _parse_cookie(cookie)
    print(f"  [suno] cookie parsed: {len(cookie)} chars")
    resp = requests.get(
        f"{CLERK_URL}?_clerk_js_version=4.73.2",
        headers={
            "Cookie"    : cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
        timeout=30,
    )
    resp.raise_for_status()
    sessions = resp.json().get("response", {}).get("sessions", [])
    if not sessions:
        raise RuntimeError("No active Suno session — please refresh SUNO_COOKIE secret")
    jwt = sessions[0].get("last_active_token", {}).get("jwt")
    if not jwt:
        raise RuntimeError("Could not extract JWT from Suno session")
    return jwt


def generate_suno_song(cookie: str, prompt: str | None = None) -> tuple[bytes, str]:
    """
    Generate a song on Suno AI and return (mp3_bytes, song_title).

    Args:
        cookie : Full browser cookie string from suno.com (stored as SUNO_COOKIE secret).
        prompt : Music prompt. Random romantic prompt used if None.

    Returns:
        (mp3_bytes, title)
    """
    if not prompt:
        prompt = random.choice(ROMANTIC_PROMPTS)

    print(f"  [suno] prompt: {prompt[:60]} ...")
    print(f"  [suno] getting session token ...")
    cookie = _parse_cookie(cookie)
    jwt = _get_jwt(cookie)

    headers = {
        "Cookie"        : cookie,
        "Authorization" : f"Bearer {jwt}",
        "Content-Type"  : "application/json",
        "User-Agent"    : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin"        : "https://suno.com",
        "Referer"       : "https://suno.com/",
    }

    # Request song generation
    print(f"  [suno] requesting generation ...")
    gen = requests.post(
        f"{SUNO_API}/generate/v2/",
        headers=headers,
        json={
            "prompt"           : prompt,
            "mv"               : "chirp-v3-5",
            "title"            : "",
            "tags"             : "romantic, love song, ballad, emotional",
            "make_instrumental": False,
            "generation_type"  : "TEXT",
        },
        timeout=60,
    )
    gen.raise_for_status()

    clips = gen.json().get("clips", [])
    if not clips:
        raise RuntimeError(f"Suno returned no clips: {gen.text[:200]}")

    clip_ids = [c["id"] for c in clips]
    print(f"  [suno] {len(clip_ids)} clip(s) queued — waiting ...")

    # Poll until generation completes
    for attempt in range(36):   # up to 6 minutes
        time.sleep(10)
        feed = requests.get(
            f"{SUNO_API}/feed/?ids={','.join(clip_ids)}",
            headers=headers, timeout=30
        ).json()

        statuses = [c.get("status", "?") for c in feed]
        print(f"  [suno] attempt {attempt+1}: {statuses}")

        if all(s == "complete" for s in statuses):
            break
        if any(s in ("error", "failed") for s in statuses):
            raise RuntimeError(f"Suno generation failed: {statuses}")
    else:
        raise RuntimeError("Suno generation timed out after 6 minutes")

    # Download best clip
    clip      = feed[0]
    title     = clip.get("title") or "Romantic Song"
    audio_url = clip.get("audio_url") or clip.get("stream_audio_url")

    if not audio_url:
        raise RuntimeError(f"No audio URL in Suno response: {clip.keys()}")

    print(f"  [suno] downloading '{title}' ...")
    mp3 = requests.get(audio_url, timeout=120)
    mp3.raise_for_status()

    print(f"  [suno] song ready: {len(mp3.content)//1024} KB ✓")
    return mp3.content, title
