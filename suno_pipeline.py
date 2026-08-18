# suno_pipeline.py (modified run() function)

import os
import time
import base64
import requests
# ... your other imports ...

# --- ACE Music API Configuration ---
ACE_MUSIC_API_KEY = os.environ.get("ACE_MUSIC_API_KEY")
ACE_API_BASE_URL = "https://api.acemusic.ai"

def generate_music_with_ace(prompt, lyrics="", duration=30, instrumental=False, language="en"):
    """
    Generate music using ACE Music's free API.
    No GPU required.
    """
    if not ACE_MUSIC_API_KEY:
        raise EnvironmentError("ACE_MUSIC_API_KEY environment variable not set.")
    
    headers = {
        "Authorization": f"Bearer {ACE_MUSIC_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Step 1: Submit the generation task
    payload = {
        "caption": prompt,
        "lyrics": lyrics,
        "audio_duration": duration,
        "instrumental": instrumental,
        "vocal_language": language,
        "thinking": True,  # Higher quality
        "audio_format": "mp3"
    }
    
    print("  [ACE] Submitting generation task...")
    response = requests.post(
        f"{ACE_API_BASE_URL}/v1/music/generate",
        json=payload,
        headers=headers,
        timeout=60
    )
    
    if response.status_code != 200:
        raise Exception(f"Task submission failed: {response.status_code} - {response.text}")
    
    result = response.json()
    job_id = result.get("job_id")
    if not job_id:
        raise Exception(f"No job_id in response: {result}")
    
    print(f"  [ACE] Task submitted. Job ID: {job_id}")
    
    # Step 2: Poll for completion
    max_attempts = 60
    for attempt in range(max_attempts):
        status_response = requests.get(
            f"{ACE_API_BASE_URL}/v1/jobs/{job_id}",
            headers=headers,
            timeout=30
        )
        
        if status_response.status_code != 200:
            print(f"  [ACE] Status check failed (attempt {attempt+1})")
            time.sleep(5)
            continue
        
        status_data = status_response.json()
        status = status_data.get("status")
        
        if status == "succeeded":
            print(f"  [ACE] Generation complete!")
            result_data = status_data.get("result", {})
            
            # Check for audio as base64
            audio_base64 = result_data.get("audio")
            if audio_base64:
                return base64.b64decode(audio_base64)
            
            # Check for audio URL
            audio_url = result_data.get("audio_url")
            if audio_url:
                audio_response = requests.get(audio_url, timeout=60)
                if audio_response.status_code == 200:
                    return audio_response.content
            
            raise Exception("No audio data found in successful response")
            
        elif status == "failed":
            error_msg = status_data.get("error", "Unknown error")
            raise Exception(f"Generation failed: {error_msg}")
        
        else:
            queue_pos = status_data.get("queue_position", "unknown")
            print(f"  [ACE] Status: {status} (queue position: {queue_pos}) - waiting...")
            time.sleep(5)
    
    raise Exception(f"Timeout after {max_attempts} attempts")


def run():
    HF_TOKEN = os.environ.get("HF_TOKEN", "")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")
    ACE_MUSIC_API_KEY = os.environ.get("ACE_MUSIC_API_KEY")  # Get the key

    if not HF_TOKEN:
        raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS:
        raise EnvironmentError("YOUTUBE_CREDENTIALS not set")
    if not ACE_MUSIC_API_KEY:
        raise EnvironmentError("ACE_MUSIC_API_KEY not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline : Romantic Song Video + Short (Weekly, Fully Automated)")
    print(f"{'='*60}\n")

    with tempfile.TemporaryDirectory(prefix="romantic_") as tmp:
        tmp = Path(tmp)
        
        # Generate lyrics
        song = generate_weekly_lyrics()
        title = song["title"]
        style_used = song.get("style", "romantic pop, female vocal, emotional")
        sections = song.get("sections") or [
            {"type": "verse", "lines": song["prompt"].split("\n")[:4]},
            {"type": "chorus", "lines": song["prompt"].split("\n")[4:8]},
        ]

        # --- NEW: Generate music with ACE Music API ---
        print("🎵  Generating music with ACE Music API...")
        
        # Build the prompt and lyrics
        music_prompt = f"{style_used}, {mood} mood"
        full_lyrics = "\n".join(["\n".join(sec.get("lines", [])) for sec in sections])
        
        # Generate the full song (vocals + instrumental)
        audio_data = generate_music_with_ace(
            prompt=music_prompt,
            lyrics=full_lyrics,
            duration=DURATION,
            instrumental=False,
            language="en"
        )
        
        # Save the generated audio
        song_mp3 = str(tmp / "generated_song.mp3")
        with open(song_mp3, "wb") as f:
            f.write(audio_data)
        
        print(f"  → Song generated: '{title}' ✓")
        
        # Skip the separate vocal/instrumental mixing steps
        # because ACE Music generates the complete song.

        # --- Continue with image generation, video creation, upload ---
        print(f"\n🖼️   Generating {n_images} romantic images ...")
        # ... rest of your image generation code ...
        
        print("\n📝  Generating SEO-optimized metadata ...")
        # ... rest of your SEO code ...
        
        print("\n📤  Uploading main video ...")
        # ... rest of your upload code ...
        
        print(f"\n🎉  Both live! Main: https://youtu.be/{vid} | Short: https://youtu.be/{short_id}")
        return vid


if __name__ == "__main__":
    run()
