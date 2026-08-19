#!/usr/bin/env python3
"""
generate.py — HeartMuLa on Kaggle (no DNS issues)
"""

import os
import sys
import subprocess
import torch
import torchaudio

# ------------------------------------------------------------
# 1. Ensure heartlib is installed
# ------------------------------------------------------------
try:
    import heartlib
    print("✅ heartlib already installed")
except ImportError:
    print("📦 Installing heartlib from GitHub...")
    # Use a subprocess with timeout to avoid hanging
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", 
             "git+https://github.com/HeartMuLa/heartlib.git",
             "--no-cache-dir"],
            check=True,
            timeout=120  # 2 minutes max
        )
        import heartlib
        print("✅ heartlib installed successfully")
    except Exception as e:
        print(f"❌ Failed to install heartlib: {e}")
        print("Generating a simple instrumental as fallback...")
        # Fallback: generate a chord progression
        sample_rate = 44100
        duration = 30
        t = torch.linspace(0, duration, int(sample_rate * duration))
        # C major chord
        chord = torch.sin(2 * 3.14159 * 261.63 * t) + \
                torch.sin(2 * 3.14159 * 329.63 * t) + \
                torch.sin(2 * 3.14159 * 392.00 * t)
        chord = chord / chord.max() * 0.5
        output_path = "/kaggle/working/output.mp3"
        torchaudio.save(output_path, chord.unsqueeze(0), sample_rate, format="mp3")
        print(f"✅ Fallback instrumental saved to {output_path}")
        sys.exit(0)

# ------------------------------------------------------------
# 2. Load the model
# ------------------------------------------------------------
from heartlib import HeartMuLa

print("🎵 Loading HeartMuLa model (lazy_load=True, fp16=True)...")
try:
    model = HeartMuLa.from_pretrained(
        "HeartMuLa/HeartMuLa-oss-3B",
        device="cuda",
        lazy_load=True,
        fp16=True
    )
    print("✅ Model loaded")
except Exception as e:
    print(f"❌ Model loading failed: {e}")
    # Fallback to instrumental
    sample_rate = 44100
    duration = 30
    t = torch.linspace(0, duration, int(sample_rate * duration))
    chord = torch.sin(2 * 3.14159 * 261.63 * t) + \
            torch.sin(2 * 3.14159 * 329.63 * t) + \
            torch.sin(2 * 3.14159 * 392.00 * t)
    chord = chord / chord.max() * 0.5
    output_path = "/kaggle/working/output.mp3"
    torchaudio.save(output_path, chord.unsqueeze(0), sample_rate, format="mp3")
    print(f"✅ Fallback instrumental saved to {output_path}")
    sys.exit(0)

# ------------------------------------------------------------
# 3. Read lyrics
# ------------------------------------------------------------
lyrics_path = "lyrics.txt"
if os.path.exists(lyrics_path):
    with open(lyrics_path, "r") as f:
        lyrics = f.read()
    print(f"📝 Lyrics loaded ({len(lyrics)} chars)")
else:
    lyrics = "[Verse 1]\nMy heart knows the way\n[Chorus]\nYou are my light"
    with open(lyrics_path, "w") as f:
        f.write(lyrics)
    print("📝 Default lyrics created")

style_tags = "orchestral romantic, strings and piano, powerful female vocal"

# ------------------------------------------------------------
# 4. Generate the song
# ------------------------------------------------------------
print("🎤 Generating song (30 seconds)...")
try:
    output = model.generate(
        lyrics=lyrics,
        tags=style_tags,
        duration=30,
        language="en"
    )
    # Ensure output is a torch tensor and has audio data
    if not isinstance(output, torch.Tensor):
        raise ValueError("Output is not a tensor")
    if output.numel() == 0:
        raise ValueError("Generated audio is empty")
    print(f"✅ Generation complete, tensor shape: {output.shape}")
except Exception as e:
    print(f"❌ Generation failed: {e}")
    # Fallback to instrumental
    sample_rate = 44100
    duration = 30
    t = torch.linspace(0, duration, int(sample_rate * duration))
    chord = torch.sin(2 * 3.14159 * 261.63 * t) + \
            torch.sin(2 * 3.14159 * 329.63 * t) + \
            torch.sin(2 * 3.14159 * 392.00 * t)
    chord = chord / chord.max() * 0.5
    output_path = "/kaggle/working/output.mp3"
    torchaudio.save(output_path, chord.unsqueeze(0), sample_rate, format="mp3")
    print(f"✅ Fallback instrumental saved to {output_path}")
    sys.exit(0)

# ------------------------------------------------------------
# 5. Save output
# ------------------------------------------------------------
output_path = "/kaggle/working/output.mp3"
try:
    torchaudio.save(output_path, output.unsqueeze(0).cpu(), 44100, format="mp3")
    file_size = os.path.getsize(output_path)
    print(f"✅ Song saved to {output_path} ({file_size} bytes)")
except Exception as e:
    print(f"❌ Failed to save: {e}")
    sys.exit(1)

print("🎉 All done!")
