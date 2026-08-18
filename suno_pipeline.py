#!/usr/bin/env python3
"""
suno_pipeline.py — Weekly Romantic Song Video + Short
FULLY AUTOMATED — uses ACE Music API (free, no GPU) to generate the full song.

Music priority:
  1. songs/ folder (manual Suno uploads — highest quality, if you add any)
  2. ACE Music API — always works, free, professional quality
"""
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime
import time
import base64
import requests

sys.path.insert(0, str(Path(__file__).parent / "src"))
from image_gen       import generate_images
from lyrics_overlay  import add_lyrics
from lyrics_writer   import generate_weekly_lyrics
from seo_gen         import generate_seo
from shorts_maker    import make_short_from_video, make_shorts_metadata
from video_assembly  import create_video
from thumbnail_gen   import create_thumbnail
from youtube_upload  import upload_to_youtube

SONGS_DIR = Path(__file__).parent / "songs"
DURATION  = 210   # seconds

BG_PROMPTS = [
    "romantic couple holding hands at golden sunset on beach, cinematic warm glow",
    "couple slow dancing in candlelit room with rose petals, soft bokeh lights",
    "two lovers on rooftop under stars, city lights below, romantic night",
    "couple under cherry blossom tree, pink petals falling, dreamy spring light",
    "man surprising woman with roses in garden, romantic golden evening",
    "couple sharing umbrella in gentle rain, warm street lights reflection",
    "silhouette of couple embracing at sunset on hill, dramatic orange sky",
    "couple sitting by lake at twilight, fairy lights on water reflection",
    "woman in red dress and man dancing at outdoor wedding, fairy lights",
    "couple on boat in misty river at dawn, mountains behind them",
    "close up of two hands intertwined, soft bokeh golden background",
    "couple watching stars lying on grass, milky way above, peaceful romantic",
    "couple in flower field at sunset, golden hour, romantic and joyful",
    "first dance at wedding with sparklers and fairy lights around them",
]

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
        "thinking": True,        # higher quality
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
            print("  [ACE] Generation complete!")
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

# --- Helper: detect mood from style text ---
def detect_mood(style_text):
    style_lower = style_text.lower()
    if "romantic" in style_lower or "love" in style_lower:
        return "romantic"
    elif "happy" in style_lower or "joy" in style_lower:
        return "happy"
    elif "sad" in style_lower or "melancholy" in style_lower:
        return "sad"
    return "neutral"

# --- Existing helper functions (unchanged) ---
def probe_duration(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","default=noprint_wrappers=1:nokey=1",path],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 180)

def get_saved_song():
    songs = sorted(SONGS_DIR.glob("*.mp3"))
    if not songs: return None, None
    idx = datetime.utcnow().timetuple().tm_yday % len(songs)
    s   = songs[idx]
    return str(s), s.stem.replace("_"," ").replace("-"," ").title()

# --- Main pipeline ---
def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN", "")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")
    ACE_MUSIC_API_KEY   = os.environ.get("ACE_MUSIC_API_KEY")   # read it here as well

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
        song_mp3 = None
        title = "Beautiful Love Song"
        style_used = ""

        # 1. Generate lyrics
        song = generate_weekly_lyrics()
        title = song["title"]
        style_used = song.get("style", "romantic pop, female vocal, emotional")
        sections = song.get("sections") or [
            {"type": "verse",  "lines": song["prompt"].split("\n")[:4]},
            {"type": "chorus", "lines": song["prompt"].split("\n")[4:8]},
        ]

        # 2. Check for saved song (manual uploads)
        saved, saved_title = get_saved_song()
        if saved:
            song_mp3 = saved
            title = saved_title
            print(f"🎵  Using saved song: {title}")

        # 3. If no saved song, generate with ACE Music API
        if not song_mp3:
            print("🎵  Generating music with ACE Music API...")
            mood = detect_mood(style_used)
            music_prompt = f"{style_used}, {mood} mood"
            full_lyrics = "\n".join(["\n".join(sec.get("lines", [])) for sec in sections])

            audio_data = generate_music_with_ace(
                prompt=music_prompt,
                lyrics=full_lyrics,
                duration=DURATION,
                instrumental=False,
                language="en"
            )

            song_mp3 = str(tmp / "generated_song.mp3")
            with open(song_mp3, "wb") as f:
                f.write(audio_data)

            print(f"  → Song generated: '{title}' ✓")

        # 4. Ensure the song is long enough (loop if needed)
        dur = probe_duration(song_mp3)
        if dur < DURATION - 10:
            looped = str(tmp / "looped.mp3")
            subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i",song_mp3,
                           "-t",str(DURATION),"-c","copy",looped],
                          check=True, capture_output=True)
            song_mp3 = looped
        dur = min(dur, DURATION)
        n_images = min(16, max(8, int(dur / 15)))

        # 5. Generate images
        print(f"\n🖼️   Generating {n_images} romantic images ...")
        prompts = [random.choice(BG_PROMPTS) for _ in range(n_images)]
        raw_imgs = generate_images(prompts, HF_TOKEN, vertical=False)

        image_paths = []
        for i, img in enumerate(raw_imgs):
            frame = add_lyrics(img, [title], "verse", "")
            p = tmp / f"frame_{i:02d}.jpg"
            p.write_bytes(frame)
            image_paths.append(str(p))

        # 6. SEO metadata
        print("\n📝  Generating SEO-optimized metadata ...")
        meta = generate_seo(title, "romantic songs", style_used)
        print(f"  → {meta['title']}")

        # 7. Thumbnail
        thumb = str(tmp / "thumbnail.jpg")
        create_thumbnail(raw_imgs[0], meta["title"], thumb)

        # 8. Main video
        video = str(tmp / "output.mp4")
        create_video(song_mp3, image_paths, video, vertical=False)

        # 9. Shorts
        print("\n📱  Creating Shorts version ...")
        short_video = str(tmp / "short.mp4")
        make_short_from_video(video, short_video, duration=55, start_offset=15)
        short_meta = make_shorts_metadata(meta["title"], meta["tags"])

        # 10. Upload main
        print("\n📤  Uploading main video ...")
        vid = upload_to_youtube(video_path=video, thumbnail_path=thumb,
            title=meta["title"], description=meta["description"],
            tags=meta["tags"], credentials_json=YOUTUBE_CREDENTIALS)
        print(f"  → https://youtu.be/{vid}")

        # 11. Upload Short
        print("\n📱  Uploading Short ...")
        short_id = upload_to_youtube(video_path=short_video, thumbnail_path=thumb,
            title=short_meta["title"], description=short_meta["description"],
            tags=short_meta["tags"], credentials_json=YOUTUBE_CREDENTIALS)
        print(f"  → https://youtu.be/{short_id}")

        print(f"\n🎉  Both live! Main: https://youtu.be/{vid} | Short: https://youtu.be/{short_id}")
        return vid


if __name__ == "__main__":
    run()
