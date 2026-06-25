"""
music_gen.py
Generates music via HuggingFace Inference API (facebook/musicgen-small).
Returns raw audio bytes — no local model download needed.
"""

import time
import requests
from requests.exceptions import ConnectionError, Timeout


HF_MODEL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
MAX_RETRIES = 8
RETRY_SLEEP  = 40   # seconds to wait while model warms up
DNS_SLEEP    = 20   # seconds to wait on DNS/connection errors
TOKEN_ESTIMATE = 256  # ~256 tokens ≈ 1 second of audio (small model)


def generate_music(prompt: str, hf_token: str, duration_sec: int = 30) -> bytes:
    """
    Generate music from a text prompt.

    Args:
        prompt      : Natural-language description of the music.
        hf_token    : HuggingFace API token (free at huggingface.co).
        duration_sec: Approximate length in seconds (default 30).

    Returns:
        Raw audio bytes (FLAC or WAV — both work with ffmpeg).
    """
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": TOKEN_ESTIMATE * duration_sec
        }
    }

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  [music] attempt {attempt}/{MAX_RETRIES} …")

        try:
            resp = requests.post(
                HF_MODEL, headers=headers, json=payload, timeout=120
            )

        except (ConnectionError, Timeout, OSError) as e:
            # DNS failure or network blip — wait and retry
            print(f"  [music] network error ({type(e).__name__}) — waiting {DNS_SLEEP}s …")
            time.sleep(DNS_SLEEP)
            continue

        if resp.status_code == 200:
            print(f"  [music] generated {len(resp.content) // 1024} KB")
            return resp.content

        if resp.status_code == 503:
            # Model is still loading on HF's side
            try:
                wait = float(resp.json().get("estimated_time", RETRY_SLEEP))
            except Exception:
                wait = RETRY_SLEEP
            wait = min(wait, 90)
            print(f"  [music] model loading — waiting {wait:.0f}s …")
            time.sleep(wait)
            continue

        if resp.status_code in (429, 500, 502, 504):
            # Rate limit or server error — wait and retry
            print(f"  [music] HTTP {resp.status_code} — waiting {DNS_SLEEP}s …")
            time.sleep(DNS_SLEEP)
            continue

        # Any other error — fail fast
        raise RuntimeError(
            f"Music generation failed [{resp.status_code}]: {resp.text[:300]}"
        )

    raise RuntimeError("Music generation: max retries exceeded.")
