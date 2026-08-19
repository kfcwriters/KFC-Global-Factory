# generate.py
import os
import torch
import torchaudio
from audiocraft.models import MusicGen

print("🚀 Booting up MusicGen on Kaggle's free GPU...")

# Load the model using the GPU
model = MusicGen.get_pretrained('facebook/musicgen-melody')
model.set_generation_params(duration=30)

prompt = "orchestral romantic, strings and piano, powerful female vocal singing"

# Generate the audio
wav = model.generate([prompt])

# Kaggle automatically saves anything written to /kaggle/working/
output_path = "/kaggle/working/output.mp3"
torchaudio.save(output_path, wav[0].cpu(), model.sample_rate, format="mp3")

print("✅ Song successfully saved to Kaggle output!")
