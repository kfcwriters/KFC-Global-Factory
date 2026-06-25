"""
music_gen.py
Generates music using the official huggingface_hub InferenceClient.
This uses the correct, current HuggingFace API endpoints automatically.
"""

import io
import time
from huggingface_hub import InferenceClient

MAX_RETRIES = 6
RETRY_SLEEP = 30


def generate_music(prompt: str, hf_token: str, duration_sec: int = 30) -> bytes:
    """
    Generate music from a text prompt using HuggingFace InferenceClient.

    Args:
        prompt      : Natural-language description of the music.
        hf_token    : HuggingFace API token.
        duration_sec: Approximate length in seconds.

    Returns:
        Raw audio bytes (works with ffmpeg).
    """
    client = InferenceClient(token=hf_token)

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  [music] attempt {attempt}/{MAX_RETRIES} …")
        try:
            result = client.text_to_audio(
                prompt,
                model="facebook/musicgen-small",
                max_new_tokens=min(256 * duration_sec, 1500),
            )

            # result is bytes
            if isinstance(result, (bytes, bytearray)):
                print(f"  [music] generated {len(result) // 1024} KB ✓")
                return bytes(result)

            # fallback: try reading as file-like
            buf = io.BytesIO()
            buf.write(result)
            data = buf.getvalue()
            print(f"  [music] generated {len(data) // 1024} KB ✓")
            return data

        except Exception as exc:
            msg = str(exc)[:200]
            print(f"  [music] attempt {attempt} failed: {msg}")
            if attempt < MAX_RETRIES:
                print(f"  [music] waiting {RETRY_SLEEP}s before retry …")
                time.sleep(RETRY_SLEEP)

    raise RuntimeError("Music generation: all retries exhausted.")
