#!/usr/bin/env python3
"""
generate.py — Minimal test on Kaggle (no pip installs)
"""
import os
import torch
import torchaudio

print("🚀 Running minimal test on Kaggle...")

# Generate a 5-second sine wave (440 Hz)
sample_rate = 44100
duration = 5
t = torch.linspace(0, duration, int(sample_rate * duration))
audio = torch.sin(2 * torch.pi * 440 * t) * 0.5

# Save as MP3
output_path = "/kaggle/working/output.mp3"
torchaudio.save(output_path, audio.unsqueeze(0), sample_rate, format="mp3")

print(f"✅ Test audio saved to {output_path}")
print(f"✅ File size: {os.path.getsize(output_path)} bytes")
