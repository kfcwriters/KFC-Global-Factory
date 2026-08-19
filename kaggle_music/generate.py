#!/usr/bin/env python3
"""
generate.py — HeartMuLa on Kaggle GPU
Generates full songs with vocals + instrumental from lyrics and style tags.
"""

import os
import subprocess
import sys
import torch
import torchaudio
import numpy as np

# ============================================================
# 1. Install heartlib if not already installed
# ============================================================
print("🚀 Setting up HeartMuLa...")

try:
    import heartlib
except ImportError:
    print("📦 Installing heartlib from GitHub...")
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "git+https://github.com/HeartMuLa/heartlib.git"
    ], check=True)
    import heartlib

from heartlib import HeartMuLa

# ============================================================
# 2. Prepare input data
# ============================================================
# Style tags (genre, mood, instruments)
style_tags = "orchestral romantic, strings and piano, powerful female vocal"

# Lyrics (use default if no file found)
lyrics_path = "lyrics.txt"
if os.path.exists(lyrics_path):
    with open(lyrics_path, "r") as f:
        lyrics = f.read()
else:
    print("⚠️ No lyrics.txt found. Using default lyrics.")
    lyrics = """
[Verse 1]
My heart knows the way
Through the darkest night

[Chorus]
You are my light
Forever by my side
"""

# ============================================================
# 3. Load model with memory-efficient settings
# ============================================================
print("🎵 Loading HeartMuLa model (lazy_load + fp16)...")
model = HeartMuLa.from_pretrained(
    "HeartMuLa/HeartMuLa-oss-3B-happy-new-year",
    device="cuda",
    lazy_load=True,      # Keeps VRAM low (~6GB)
    fp16=True            # Faster and memory-efficient
)

# ============================================================
# 4. Generate the full song
# ============================================================
print("🎤 Generating song... (this takes 2-4 minutes)")
output = model.generate(
    lyrics=lyrics,
    tags=style_tags,
    duration=30,         # Seconds – increase for longer songs
    language="en"
)

# ============================================================
# 5. Save as MP3
# ============================================================
output_path = "/kaggle/working/output.mp3"
torchaudio.save(
    output_path,
    output.unsqueeze(0).cpu(),
    sample_rate=44100,
    format="mp3"
)

print(f"✅ Song saved to {output_path}")
