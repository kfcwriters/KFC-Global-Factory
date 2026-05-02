from audiocraft.models import MusicGen
import scipy.io.wavfile
import torch
import os

# Create a professional romantic 25-second song
model = MusicGen.get_pretrained('facebook/musicgen-small')
model.set_generation_params(duration=25)

descriptions = ['romantic haryanvi lo-fi beat with soft flute melody']
wav = model.generate(descriptions)

# Save as high-quality WAV
scipy.io.wavfile.write('ai_song.wav', rate=32000, data=wav[0, 0].cpu().numpy())
print("✅ Music Generated Successfully")
