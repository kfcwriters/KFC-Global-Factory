#!/usr/bin/env python3
"""
generate.py — HeartMuLa on Kaggle GPU
"""

import os
import subprocess
import sys
import torch
import torchaudio

print("🚀 Setting up HeartMuLa...")

# Install heartlib if needed
try:
    import heartlib
except ImportError:
    print("📦 Installing heartlib...")
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "git+https://github.com/HeartMuLa/heartlib.git"
    ], check=True)
    import heartlib

from heartlib import HeartMuLa

# Read lyrics from file
lyrics_path = "lyrics.txt"
if os.path.exists(lyrics_path):
    with open(lyrics_path, "r") as f:
        lyrics = f.read()
    print(f"📝 Lyrics loaded ({len(lyrics)} chars)")
else:
    print("⚠️ No lyrics.txt found. Using default.")
    lyrics = """
[Verse 1]
My heart knows the way
Through the darkest night

[Chorus]
You are my light
Forever by my side
"""

style_tags = "orchestral romantic, strings and piano, powerful female vocal"

print("🎵 Loading HeartMuLa model...")
model = HeartMuLa.from_pretrained(
    "HeartMuLa/HeartMuLa-oss-3B-happy-new-year",
    device="cuda",
    lazy_load=True,
    fp16=True
)

print("🎤 Generating song... (takes 2-4 minutes)")
output = model.generate(
    lyrics=lyrics,
    tags=style_tags,
    duration=30,
    language="en"
)

output_path = "/kaggle/working/output.mp3"
torchaudio.save(
    output_path,
    output.unsqueeze(0).cpu(),
    sample_rate=44100,
    format="mp3"
)

print(f"✅ Song saved to {output_path}")
