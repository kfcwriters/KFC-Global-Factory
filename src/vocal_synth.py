# src/vocal_synth.py – Free singing synthesis using Bark via Hugging Face Inference API
import os
import requests
import json
import numpy as np
import scipy.io.wavfile as wavfile
from io import BytesIO

HF_TOKEN = os.environ.get("HF_TOKEN", "")
BARK_URL = "https://api-inference.huggingface.co/models/suno/bark"

# Map your mood strings to descriptive singing styles
MOOD_STYLE = {
    "romantic": "soft, emotional, slow",
    "happy": "bright, cheerful, upbeat",
    "sad": "melancholic, gentle, longing",
    "default": "neutral"
}

def detect_mood(style_text):
    # This is already imported from vocal_synth in your main script
    # We'll keep the same logic here for completeness
    style_lower = style_text.lower()
    if "romantic" in style_lower or "love" in style_lower:
        return "romantic"
    elif "happy" in style_lower or "joy" in style_lower:
        return "happy"
    elif "sad" in style_lower or "melancholy" in style_lower:
        return "sad"
    return "default"

def sing_lyrics(sections, mood="romantic", tempo_bpm=120):
    """
    Generate singing audio from lyrics sections using Bark via HF Inference API.
    Returns WAV bytes.
    """
    if not HF_TOKEN:
        raise EnvironmentError("HF_TOKEN not set – cannot call Bark API.")

    # Build a single prompt from all sections
    full_lyrics = []
    for sec in sections:
        lines = sec.get("lines", [])
        if lines:
            full_lyrics.extend(lines)
    text = " ".join(full_lyrics)

    # Add musical style and singing instructions
    style_desc = MOOD_STYLE.get(mood, "neutral")
    prompt = f"♪ ({style_desc} singing, {tempo_bpm} bpm) {text} ♪"

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}

    # Call Bark
    response = requests.post(BARK_URL, headers=headers, json=payload, timeout=120)

    if response.status_code == 200:
        # Bark returns raw audio bytes (PCM 16-bit, 24kHz) – but we need WAV.
        # The API returns audio/wav content directly.
        # However, the HF inference for Bark returns a binary audio file.
        # We can just return the bytes as is (it's already a WAV).
        # But to be safe, we can validate that it's a WAV by checking header.
        audio_bytes = response.content
        # Optionally, we could resample to match your expected sample rate.
        # Your pipeline uses 44.1kHz for mixing; we'll let ffmpeg handle it.
        return audio_bytes
    else:
        print(f"❌ Bark API failed: {response.status_code} - {response.text}")
        # Fallback: generate a simple sine wave tone (so pipeline doesn't crash)
        print("⚠️  Using fallback sine tone (no vocals)")
        return generate_fallback_audio(3.0)  # 3 seconds of beep

def generate_fallback_audio(duration_sec=3.0, sample_rate=44100):
    """Generate a simple sine wave as fallback."""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec))
    audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # 440 Hz
    audio = (audio * 32767).astype(np.int16)
    buf = BytesIO()
    wavfile.write(buf, sample_rate, audio)
    return buf.getvalue()
