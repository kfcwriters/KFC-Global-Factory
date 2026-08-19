#!/usr/bin/env python3
"""
yue_generator.py — Generate songs using YuE via a public Hugging Face Space.
No API key required — uses gradio_client to interact with the free demo.
"""
import sys
import os
import shutil
import time
from pathlib import Path
from gradio_client import Client

# The public Hugging Face Space hosting YuE
SPACE_ID = "innova-ai/YuE-music-generator-demo"

def generate_song():
    print(f"🔗 Connecting to public YuE Space: {SPACE_ID}...")
    
    # --- You can customize these prompts ---
    genre_prompt = "orchestral romantic, strings and piano, powerful female vocal"
    lyrics_prompt = """[Verse 1]
My heart knows the way
Through the darkest night

[Chorus]
You are my light
Forever by my side"""
    
    try:
        # Connect to the public Space (no API key needed)
        client = Client(SPACE_ID)
        print("🎵 Submitting lyrics... (Waiting in the public GPU queue)")
        print("⏳ This may take 2-5 minutes depending on queue length.")
        
        # The specific parameters expected by the YuE Gradio demo
        result = client.predict(
            genre_txt=genre_prompt,
            lyrics_txt=lyrics_prompt,
            run_n_segments=2,       # Number of lyric sections
            stage2_batch_size=4,    # Speed parameter
            api_name="/generate"
        )
        
        # Gradio spaces often return a tuple with the audio file path
        audio_path = result[1] if isinstance(result, tuple) else result
        
        print(f"✅ Audio generated! File: {audio_path}")
        
        # Create the target directory
        target_dir = Path("temp_audio")
        target_dir.mkdir(exist_ok=True)
        target_path = target_dir / "output.mp3"
        
        # Move the generated file to where GitHub Actions expects it
        if os.path.exists(audio_path):
            shutil.move(audio_path, str(target_path))
            print(f"✅ YuE Song successfully saved to {target_path}")
        else:
            print(f"❌ Audio file not found at {audio_path}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Failed to generate song via Hugging Face Space: {e}")
        print("The Space might be asleep or overloaded. Try again later.")
        sys.exit(1)

if __name__ == "__main__":
    generate_song()
