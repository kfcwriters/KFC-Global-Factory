#!/usr/bin/env python3
"""
generate.py — HeartMuLa on Kaggle GPU
Generates full songs with vocals + instrumental from lyrics and style tags.
Includes robust error handling and explicit dependency installation.
"""

import os
import sys
import subprocess
import torch
import torchaudio

print("🚀 Setting up HeartMuLa on Kaggle GPU...")

# ============================================================
# 1. Install dependencies explicitly
# ============================================================
print("📦 Installing required packages...")
subprocess.run([
    sys.executable, "-m", "pip", "install",
    "torch", "torchaudio", "transformers",
    "accelerate", "sentencepiece", "protobuf",
    "heartlib", "soundfile", "librosa",
    "--upgrade", "--no-cache-dir"
], check=True, capture_output=False)

# ============================================================
# 2. Import heartlib
# ============================================================
try:
    from heartlib import HeartMuLa
    print("✅ heartlib imported successfully")
except ImportError as e:
    print(f"❌ Failed to import heartlib: {e}")
    print("Trying fallback installation from GitHub...")
    subprocess.run([
        sys.executable, "-m", "pip", "install",
        "git+https://github.com/HeartMuLa/heartlib.git"
    ], check=True)
    from heartlib import HeartMuLa
    print("✅ heartlib installed from GitHub")

# ============================================================
# 3. Read lyrics
# ============================================================
lyrics_path = "lyrics.txt"
if os.path.exists(lyrics_path):
    with open(lyrics_path, "r") as f:
        lyrics = f.read()
    print(f"📝 Lyrics loaded ({len(lyrics)} chars)")
else:
    print("⚠️ No lyrics.txt found, using default lyrics.")
    lyrics = """
[Verse 1]
My heart knows the way
Through the darkest night

[Chorus]
You are my light
Forever by my side
"""
    # Write default for debugging
    with open(lyrics_path, "w") as f:
        f.write(lyrics)
    print("✅ Default lyrics written to lyrics.txt")

# ============================================================
# 4. Style tags
# ============================================================
style_tags = "orchestral romantic, strings and piano, powerful female vocal"

# ============================================================
# 5. Load model with memory-efficient settings
# ============================================================
print("🎵 Loading HeartMuLa model...")
try:
    model = HeartMuLa.from_pretrained(
        "HeartMuLa/HeartMuLa-oss-3B",
        device="cuda",
        lazy_load=True,    # Reduces VRAM to ~6.2GB
        fp16=True          # Faster and more memory-efficient
    )
    print("✅ Model loaded successfully")
    print(f"   Device: {model.device}")
except Exception as e:
    print(f"❌ Model loading failed: {e}")
    print("Trying alternative model ID...")
    try:
        model = HeartMuLa.from_pretrained(
            "HeartMuLa/HeartMuLa-oss-3B-happy-new-year",
            device="cuda",
            lazy_load=True,
            fp16=True
        )
        print("✅ Alternative model loaded successfully")
    except Exception as e2:
        print(f"❌ Both models failed: {e2}")
        sys.exit(1)

# ============================================================
# 6. Generate the song
# ============================================================
print("🎤 Generating song... (this takes 2-4 minutes)")
try:
    output = model.generate(
        lyrics=lyrics,
        tags=style_tags,
        duration=30,        # Seconds – increase for longer songs
        language="en"
    )
    print(f"✅ Generation complete, output tensor shape: {output.shape}")
except Exception as e:
    print(f"❌ Generation failed: {e}")
    sys.exit(1)

# ============================================================
# 7. Save as MP3
# ============================================================
output_path = "/kaggle/working/output.mp3"
try:
    torchaudio.save(
        output_path,
        output.unsqueeze(0).cpu(),
        sample_rate=44100,
        format="mp3"
    )
    print(f"✅ Song saved to {output_path}")
    print(f"✅ File size: {os.path.getsize(output_path)} bytes")
except Exception as e:
    print(f"❌ Failed to save audio: {e}")
    sys.exit(1)

print("🎉 All done! The song is ready in /kaggle/working/output.mp3")
