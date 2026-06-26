"""
music_gen.py
Generates music using huggingface_hub InferenceClient.
Uses post() which works in ALL versions, with text_to_audio as preferred method.
"""
import time
from huggingface_hub import InferenceClient


MAX_RETRIES = 6
RETRY_SLEEP = 30
MUSIC_MODEL = "facebook/musicgen-small"


def generate_music(prompt: str, hf_token: str, duration_sec: int = 30) -> bytes:
    client     = InferenceClient(token=hf_token)
    max_tokens = min(256 * duration_sec, 1500)

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"  [music] attempt {attempt}/{MAX_RETRIES} …")
        try:
            # text_to_audio exists in huggingface_hub >= 0.18
            # post() exists in ALL versions — safe universal fallback
            if hasattr(client, "text_to_audio"):
                result = client.text_to_audio(
                    prompt,
                    model=MUSIC_MODEL,
                    max_new_tokens=max_tokens,
                )
            else:
                result = client.post(
                    json={"inputs": prompt,
                          "parameters": {"max_new_tokens": max_tokens}},
                    model=MUSIC_MODEL,
                )

            audio = bytes(result) if isinstance(result, (bytes, bytearray)) else result
            print(f"  [music] generated {len(audio) // 1024} KB ✓")
            return audio

        except Exception as exc:
            print(f"  [music] attempt {attempt} failed: {str(exc)[:200]}")
            if attempt < MAX_RETRIES:
                print(f"  [music] waiting {RETRY_SLEEP}s …")
                time.sleep(RETRY_SLEEP)

    raise RuntimeError("Music generation: all retries exhausted.")
