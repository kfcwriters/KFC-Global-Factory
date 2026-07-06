"""
Generates a music clip from a text prompt using HuggingFace's free
Inference API (facebook/musicgen-small).

Note: HF's free serverless inference can be slow to "warm up" (503s)
or occasionally rate-limited / gated behind a PRO plan depending on
current HF policy — this module retries with backoff and falls back
to a procedurally generated ambient tone (via numpy/scipy) if the API
is unavailable, so the pipeline never hard-fails.
"""
import os
import time
import requests
import numpy as np
from scipy.io import wavfile

HF_TOKEN = os.environ.get("HF_TOKEN")
MUSICGEN_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"


def _procedural_fallback(out_path: str, duration_sec: int = 30, sample_rate: int = 32000):
    """Generates a simple, calm ambient pad tone as a last-resort fallback
    so the pipeline can still finish a video even if MusicGen is down."""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    freqs = [220, 277.18, 329.63]  # A minor-ish soft chord
    wave = sum(np.sin(2 * np.pi * f * t) for f in freqs) / len(freqs)
    fade_len = int(sample_rate * 2)
    fade = np.linspace(0, 1, fade_len)
    wave[:fade_len] *= fade
    wave[-fade_len:] *= fade[::-1]
    wave = (wave * 0.3 * 32767).astype(np.int16)
    wavfile.write(out_path, sample_rate, wave)
    print("  [fallback] Used procedural ambient tone instead of MusicGen.")


def generate_music(prompt: str, out_path: str, duration_sec: int = 30, retries: int = 6):
    if not HF_TOKEN:
        print("  HF_TOKEN not set — using procedural fallback.")
        _procedural_fallback(out_path, duration_sec)
        return

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}

    for attempt in range(1, retries + 1):
        resp = requests.post(MUSICGEN_URL, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("audio"):
            with open(out_path, "wb") as f:
                f.write(resp.content)
            return
        if resp.status_code == 503:
            wait = min(20 * attempt, 90)
            print(f"  MusicGen warming up (attempt {attempt}/{retries}), waiting {wait}s...")
            time.sleep(wait)
            continue
        print(f"  MusicGen error {resp.status_code}: {resp.text[:200]}")
        time.sleep(5)

    print("  MusicGen unavailable after retries — using procedural fallback.")
    _procedural_fallback(out_path, duration_sec)


if __name__ == "__main__":
    generate_music(
        "gentle healing ambient music with soft piano",
        out_path="test_music.wav",
    )
