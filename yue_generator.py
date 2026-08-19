import sys
import shutil
import os
from gradio_client import Client

# A list of exact clones of the YuE Space. 
# The script will try them one by one until it finds a working GPU.
BACKUP_SPACES = [
    "Alissonerdx/YuE-music-generator",     # Community clone 1
    "multimodalart/YuE",                   # Community clone 2
    "m-a-p/YuE-explorer",                  # Official space
    "innova-ai/YuE-music-generator-demo"   # The one that is currently broken
]

def generate_song():
    genre_prompt = "orchestral romantic, strings and piano, powerful female vocal"
    lyrics_prompt = "[Verse 1]\nMy heart knows the way\nThrough the darkest night\n\n[Chorus]\nYou are my light\nForever by my side"
    
    for space_id in BACKUP_SPACES:
        print(f"🔗 Attempting to connect to Space: {space_id}...")
        try:
            client = Client(space_id)
            print("🎵 Submitting lyrics... (Waiting in the public GPU queue)")
            
            # Since these are clones, the api parameters are identical
            result = client.predict(
                genre_txt=genre_prompt,
                lyrics_txt=lyrics_prompt,
                run_n_segments=2,       
                stage2_batch_size=4,    
                api_name="/generate"
            )
            
            # Extract the audio file path
            audio_path = result[1] if isinstance(result, tuple) else result
            
            # Move it to where GitHub Actions expects it
            os.makedirs(os.path.dirname("temp_audio/output.mp3"), exist_ok=True)
            shutil.move(audio_path, "temp_audio/output.mp3")
            
            print(f"✅ Song successfully generated using {space_id}!")
            return # Exit successfully without trying the rest

        except Exception as e:
            print(f"⚠️ Failed on {space_id}: {e}")
            print("Moving to the next backup space...\n")
            
    # If it goes through the entire list and they all fail
    print("❌ All free Hugging Face Spaces are currently offline or overloaded.")
    sys.exit(1)

if __name__ == "__main__":
    generate_song()
