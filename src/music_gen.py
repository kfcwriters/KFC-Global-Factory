"""
music_gen.py
Primary  : HuggingFace API (direct requests)
Fallback : Karplus-Strong string synthesis — sounds like piano/harp, not beeps
"""
import io, time, random, math
import numpy as np
import scipy.io.wavfile as wavfile
import requests

HF_ENDPOINTS = [
    "https://router.huggingface.co/hf-inference/models/facebook/musicgen-small",
    "https://api-inference.huggingface.co/models/facebook/musicgen-small",
]
SR = 44100   # sample rate

# Pentatonic scale notes (Hz) — pleasant, no dissonance
PENTATONIC = [
    130.81, 146.83, 164.81, 196.00, 220.00,   # C3-A3
    261.63, 293.66, 329.63, 392.00, 440.00,   # C4-A4
    523.25, 587.33, 659.25, 783.99, 880.00,   # C5-G5
]

# Mood presets: (bass_hz, note_pool_slice, note_spacing_sec, decay)
MOODS = {
    "sleep"     : (55,  PENTATONIC[:6],  3.5, 0.9990),
    "meditation": (65,  PENTATONIC[:8],  3.0, 0.9985),
    "healing"   : (74,  PENTATONIC[:8],  2.8, 0.9988),
    "lofi"      : (98,  PENTATONIC[4:12], 1.8, 0.9970),
    "focus"     : (110, PENTATONIC[4:12], 2.0, 0.9975),
    "romantic"  : (82,  PENTATONIC[2:10], 2.5, 0.9982),
    "default"   : (82,  PENTATONIC[3:11], 2.5, 0.9980),
}


def generate_music(prompt: str, hf_token: str, duration_sec: int = 30) -> bytes:
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt,
               "parameters": {"max_new_tokens": min(256 * duration_sec, 1500)}}

    for url in HF_ENDPOINTS:
        print(f"  [music] trying {url.split('/')[2]} …")
        for attempt in range(1, 4):
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=120)
                if r.status_code == 200:
                    print(f"  [music] HuggingFace OK ({len(r.content)//1024} KB) ✓")
                    return r.content
                elif r.status_code == 503:
                    try:    wait = float(r.json().get("estimated_time", 40))
                    except: wait = 40
                    time.sleep(min(wait, 60))
                else:
                    print(f"  [music] HTTP {r.status_code} — next endpoint")
                    break
            except Exception as e:
                print(f"  [music] attempt {attempt}: {str(e)[:80]}")
                time.sleep(15)

    print("  [music] HuggingFace unavailable — synthesising music locally …")
    return _synthesise(prompt, duration_sec)


# ──────────────────────────────────────────────
# Karplus-Strong string synthesis
# ──────────────────────────────────────────────

def _karplus_strong(freq: float, dur: float, decay: float = 0.998) -> np.ndarray:
    """Generate a plucked-string note (piano / harp-like tone)."""
    n      = int(SR * dur)
    period = max(int(SR / freq), 2)
    buf    = np.random.randn(period).astype(np.float32) * 0.8
    out    = np.zeros(n, np.float32)
    for i in range(n):
        out[i]       = buf[i % period]
        buf[i%period] = decay * 0.5 * (buf[i%period] + buf[(i+1)%period])
    # soft attack
    attack = min(int(SR * 0.01), n)
    out[:attack] *= np.linspace(0, 1, attack)
    return out


def _get_mood(prompt: str) -> tuple:
    p = prompt.lower()
    for key, val in MOODS.items():
        if key in p:
            return val
    return MOODS["default"]


def _synthesise(prompt: str, duration_sec: int = 45) -> bytes:
    bass_hz, note_pool, spacing, decay = _get_mood(prompt)
    n = int(SR * duration_sec)
    t = np.linspace(0, duration_sec, n, dtype=np.float32)
    audio = np.zeros(n, np.float32)

    # ── Melody: plucked notes ──────────────────
    note_dur  = spacing * 2.5   # each note rings longer than gap
    pos_sec   = 1.0
    while pos_sec < duration_sec - note_dur:
        freq  = random.choice(note_pool)
        note  = _karplus_strong(freq, note_dur, decay)
        start = int(pos_sec * SR)
        end   = min(start + len(note), n)
        audio[start:end] += note[:end - start] * 0.45
        pos_sec += spacing + random.uniform(-0.3, 0.5)

    # ── Bass drone (warm undertone) ────────────
    drone  = 0.12 * np.sin(2*math.pi * bass_hz       * t)
    drone += 0.07 * np.sin(2*math.pi * bass_hz * 1.5 * t)
    drone += 0.04 * np.sin(2*math.pi * bass_hz * 2.0 * t)
    # slow "breathing" modulation on the drone
    mod    = 0.6 + 0.4 * np.sin(2*math.pi * 0.08 * t)
    audio += drone * mod

    # ── Soft pink noise (air / warmth) ────────
    noise = np.random.randn(n).astype(np.float32) * 0.018
    for k in range(1, n):
        noise[k] = 0.94 * noise[k-1] + 0.06 * noise[k]
    audio += noise

    # ── Normalise ─────────────────────────────
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.80

    # ── Fade in / out (3 s) ───────────────────
    fade = min(int(SR * 3), n // 4)
    audio[:fade]  *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)

    # ── Encode to WAV bytes ───────────────────
    buf = io.BytesIO()
    wavfile.write(buf, SR, (audio * 32767).astype(np.int16))
    data = buf.getvalue()
    print(f"  [music] synthesised locally ({len(data)//1024} KB) ✓")
    return data
