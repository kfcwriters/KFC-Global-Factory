"""
music_gen.py
Primary  : HuggingFace Serverless Inference API (direct requests, no huggingface_hub)
Fallback : Procedural ambient music generator (numpy + scipy) — always works
"""
import io
import time
import math
import random
import requests
import numpy as np
import scipy.io.wavfile as wavfile


# Try both HuggingFace endpoints (new router first, then legacy)
HF_ENDPOINTS = [
    "https://router.huggingface.co/hf-inference/models/facebook/musicgen-small",
    "https://api-inference.huggingface.co/models/facebook/musicgen-small",
]
SAMPLE_RATE = 44100


def generate_music(prompt: str, hf_token: str, duration_sec: int = 30) -> bytes:
    """
    Generate music. Tries HuggingFace API first, falls back to
    procedural ambient generation (always succeeds).
    """
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": min(256 * duration_sec, 1500)}
    }

    for url in HF_ENDPOINTS:
        print(f"  [music] trying {url.split('/')[2]} …")
        for attempt in range(1, 4):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=120)
                if resp.status_code == 200:
                    print(f"  [music] HuggingFace OK ({len(resp.content)//1024} KB) ✓")
                    return resp.content
                elif resp.status_code == 503:
                    try:
                        wait = float(resp.json().get("estimated_time", 40))
                    except Exception:
                        wait = 40
                    print(f"  [music] model loading, waiting {min(wait,60):.0f}s …")
                    time.sleep(min(wait, 60))
                else:
                    print(f"  [music] HTTP {resp.status_code} — skipping endpoint")
                    break
            except Exception as exc:
                print(f"  [music] attempt {attempt}: {str(exc)[:100]}")
                time.sleep(15)

    # ── Fallback: generate ambient music procedurally ──────────────────────────
    print("  [music] HuggingFace unavailable — generating ambient music locally …")
    return _generate_ambient(prompt, duration_sec)


# ─────────────────────────────────────────
# Procedural ambient music generator
# ─────────────────────────────────────────

# Frequency sets per mood keyword
MOOD_FREQS = {
    "sleep":      [40, 55, 80, 110],
    "meditation": [128, 136, 144, 192],
    "healing":    [174, 285, 396, 528],
    "focus":      [200, 400, 600, 800],
    "lofi":       [130, 196, 261, 392],
    "default":    [80, 120, 160, 240],
}


def _get_freqs(prompt: str) -> list:
    p = prompt.lower()
    for key in MOOD_FREQS:
        if key in p:
            return MOOD_FREQS[key]
    return MOOD_FREQS["default"]


def _generate_ambient(prompt: str, duration_sec: int = 45) -> bytes:
    """Generate layered ambient drone music matching the prompt mood."""
    n      = int(SAMPLE_RATE * duration_sec)
    t      = np.linspace(0, duration_sec, n, dtype=np.float32)
    audio  = np.zeros(n, dtype=np.float32)
    freqs  = _get_freqs(prompt)

    for i, freq in enumerate(freqs):
        amp       = 0.18 / (i + 1)
        phase     = random.random() * 2 * math.pi
        # Slow amplitude modulation — "breathing" effect
        mod_rate  = 0.05 + i * 0.03
        mod       = 0.6 + 0.4 * np.sin(2 * math.pi * mod_rate * t)
        audio    += amp * mod * np.sin(2 * math.pi * freq * t + phase)
        # Add subtle harmonic
        audio    += (amp * 0.3) * mod * np.sin(2 * math.pi * freq * 2 * t + phase)

    # Soft pink noise (warmth / rain-like texture)
    noise = np.random.randn(n).astype(np.float32) * 0.04
    for k in range(1, n):
        noise[k] = 0.92 * noise[k-1] + 0.08 * noise[k]
    audio += noise

    # Normalise to 80% peak
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.80

    # 3-second fade in / fade out
    fade = min(int(SAMPLE_RATE * 3), n // 4)
    audio[:fade]  *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)

    # Encode to WAV bytes
    audio_int16 = (audio * 32767).astype(np.int16)
    buf = io.BytesIO()
    wavfile.write(buf, SAMPLE_RATE, audio_int16)
    data = buf.getvalue()
    print(f"  [music] ambient generated locally ({len(data)//1024} KB) ✓")
    return data
