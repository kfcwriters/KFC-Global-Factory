#!/usr/bin/env python3
"""
suno_pipeline.py — Weekly Romantic Song Video + Short
Uses Boson AI Higgs Audio (singing generation) – free, rate-limited public preview.
No GPU required, works with GitHub Actions.
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
import json

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
DURATION  = 210

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

# --- Boson AI Higgs Audio Configuration ---
BOSON_API_KEY = os.environ.get("BOSON_API_KEY")

def generate_song_boson(prompt, lyrics="", duration=30, voice="female-1"):
    """
    Generate singing audio using Boson AI Higgs Audio.
    Tries multiple possible endpoints to handle API changes.
    Free, rate-limited public preview. No GPU needed.
    """
    if not BOSON_API_KEY:
        raise EnvironmentError("BOSON_API_KEY environment variable not set.")
    
    headers = {
        "Authorization": f"Bearer {BOSON_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Possible endpoints based on common patterns and docs
    endpoints = [
        "https://api.boson.ai/v1/higgs-audio/tts",
        "https://api.boson.ai/v1/higgs-audio/generate",
        "https://api.boson.ai/v1/audio/tts",
        "https://api.boson.ai/v1/audio/generate",
        "https://api.boson.ai/v1/chat/completions",  # Some use this with audio
    ]
    
    # Try different payload structures
    payloads = [
        # Standard TTS payload
        {"text": lyrics, "prompt": prompt, "style": "singing", "voice": voice, "duration": duration, "response_format": "mp3"},
        # Alternative: use "input" instead of "text"
        {"input": lyrics, "prompt": prompt, "style": "singing", "voice": voice, "duration": duration, "response_format": "mp3"},
        # For chat completions style (if supported)
        {"model": "higgs-audio", "messages": [{"role": "user", "content": f"{prompt}\n\n{lyrics}"}], "style": "singing", "duration": duration}
    ]
    
    last_error = None
    for endpoint in endpoints:
        for payload in payloads:
            try:
                print(f"  [Boson] Trying {endpoint} with payload keys: {list(payload.keys())}")
                response = requests.post(endpoint, json=payload, headers=headers, timeout=120)
                if response.status_code == 200:
                    data = response.json()
                    # Extract audio from various possible fields
                    audio_b64 = data.get("audio") or data.get("data", {}).get("audio") or data.get("output", {}).get("audio")
                    if audio_b64:
                        return base64.b64decode(audio_b64)
                    audio_url = data.get("audio_url") or data.get("data", {}).get("audio_url") or data.get("output", {}).get("audio_url")
                    if audio_url:
                        audio_resp = requests.get(audio_url, timeout=60)
                        if audio_resp.status_code == 200:
                            return audio_resp.content
                    # If audio is in a different field, try to find it
                    if "choices" in data and data["choices"]:
                        choice = data["choices"][0]
                        audio_b64 = choice.get("message", {}).get("audio")
                        if audio_b64:
                            return base64.b64decode(audio_b64)
                    # If all fail, raise
                    raise Exception("No audio found in successful response")
                else:
                    if response.status_code != 404:
                        print(f"  [Boson] {endpoint} returned {response.status_code}: {response.text[:100]}")
                    last_error = f"{response.status_code} - {response.text[:200]}"
            except Exception as e:
                print(f"  [Boson] Error with {endpoint}: {e}")
                last_error = str(e)
            time.sleep(0.2)  # brief pause between attempts
    
    # If all endpoints failed, try the old ACE Music API as a fallback if token exists
    ace_token = os.environ.get("ACE_SESSION_TOKEN")
    if ace_token:
        print("  [Boson] All endpoints failed. Trying ACE Music API as fallback...")
        try:
            return generate_music_ace_fallback(prompt, lyrics, duration)
        except Exception as e:
            print(f"  [Fallback] ACE failed: {e}")
    
    raise Exception(f"All Boson endpoints failed. Last error: {last_error}")

def generate_music_ace_fallback(prompt, lyrics="", duration=30):
    """
    Fallback to ACE Music API if Boson fails and we have a session token.
    """
    token = os.environ.get("ACE_SESSION_TOKEN")
    if not token:
        raise Exception("ACE_SESSION_TOKEN not set for fallback")
    
    headers = {
        "Origin": "https://acemusic.ai",
        "Referer": "https://acemusic.ai/",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {
        "task_type": "generate",
        "model_type": "acestep-v15-xl-turbo",
        "prompt": prompt,
        "lyrics": lyrics,
        "duration": str(duration),
        "instrumental": "false",
        "vocal_language": "en",
        "thinking": "true",
        "audio_format": "mp3",
        "mode": "simple",
        "ai_token": token,
        "app": "studio-web",
        "sample_mode": "false",
        "seed": "-1",
    }
    resp = requests.post(
        "https://ai-api.acemusic.ai/engine/api/engine/release_task",
        data=data,
        headers=headers,
        timeout=60
    )
    if resp.status_code != 200:
        raise Exception(f"ACE fallback failed: {resp.status_code}")
    result = resp.json()
    task_id = result.get("task_id")
    if not task_id:
        raise Exception("No task_id from ACE")
    # Poll for result (simplified)
    for _ in range(30):
        status = requests.get(
            f"https://ai-api.acemusic.ai/engine/api/engine/status",
            params={"task_id": task_id},
            headers=headers
        )
        if status.status_code != 200:
            time.sleep(5)
            continue
        status_data = status.json()
        if status_data.get("status") == "succeeded":
            result_resp = requests.get(
                f"https://ai-api.acemusic.ai/engine/api/engine/query_result",
                params={"task_id": task_id},
                headers=headers
            )
            if result_resp.status_code == 200:
                result_data = result_resp.json()
                audio_b64 = result_data.get("audio") or result_data.get("data", {}).get("audio")
                if audio_b64:
                    return base64.b64decode(audio_b64)
                audio_url = result_data.get("audio_url")
                if audio_url:
                    audio = requests.get(audio_url)
                    if audio.status_code == 200:
                        return audio.content
            break
        time.sleep(5)
    raise Exception("ACE fallback timed out")

# --- Helper functions (unchanged) ---
def detect_mood(style_text):
    style_lower = style_text.lower()
    if "romantic" in style_lower or "love" in style_lower:
        return "romantic"
    elif "happy" in style_lower or "joy" in style_lower:
        return "happy"
    elif "sad" in style_lower or "melancholy" in style_lower:
        return "sad"
    return "neutral"

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
    BOSON_API_KEY       = os.environ.get("BOSON_API_KEY")

    if not HF_TOKEN:
        raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS:
        raise EnvironmentError("YOUTUBE_CREDENTIALS not set")
    if not BOSON_API_KEY:
        raise EnvironmentError("BOSON_API_KEY not set")

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
            {"type": "verse",  "lines": song["prompt"].split("\n")[:4]},
            {"type": "chorus", "lines": song["prompt"].split("\n")[4:8]},
        ]

        # Try saved song first (manual uploads)
        saved, saved_title = get_saved_song()
        if saved:
            song_mp3 = saved
            title = saved_title
            print(f"🎵  Using saved song: {title}")
        else:
            print("🎵  Generating singing with Boson AI Higgs Audio...")
            mood = detect_mood(style_used)
            music_prompt = f"{style_used}, {mood} mood"
            full_lyrics = "\n".join(["\n".join(sec.get("lines", [])) for sec in sections])

            # Generate audio via Boson AI
            audio_data = generate_song_boson(
                prompt=music_prompt,
                lyrics=full_lyrics,
                duration=DURATION,
                voice="female-1"
            )

            song_mp3 = str(tmp / "generated_song.mp3")
            with open(song_mp3, "wb") as f:
                f.write(audio_data)

            print(f"  → Song generated: '{title}' ✓")

        # Loop if needed
        dur = probe_duration(song_mp3)
        if dur < DURATION - 10:
            looped = str(tmp / "looped.mp3")
            subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i",song_mp3,
                           "-t",str(DURATION),"-c","copy",looped],
                          check=True, capture_output=True)
            song_mp3 = looped
        dur = min(dur, DURATION)
        n_images = min(16, max(8, int(dur / 15)))

        # Generate images
        print(f"\n🖼️   Generating {n_images} romantic images ...")
        prompts = [random.choice(BG_PROMPTS) for _ in range(n_images)]
        raw_imgs = generate_images(prompts, HF_TOKEN, vertical=False)

        image_paths = []
        for i, img in enumerate(raw_imgs):
            frame = add_lyrics(img, [title], "verse", "")
            p = tmp / f"frame_{i:02d}.jpg"
            p.write_bytes(frame)
            image_paths.append(str(p))

        print("\n📝  Generating SEO-optimized metadata ...")
        meta = generate_seo(title, "romantic songs", style_used)
        print(f"  → {meta['title']}")

        thumb = str(tmp / "thumbnail.jpg")
        create_thumbnail(raw_imgs[0], meta["title"], thumb)
        video = str(tmp / "output.mp4")
        create_video(song_mp3, image_paths, video, vertical=False)

        print("\n📱  Creating Shorts version ...")
        short_video = str(tmp / "short.mp4")
        make_short_from_video(video, short_video, duration=55, start_offset=15)
        short_meta = make_shorts_metadata(meta["title"], meta["tags"])

        print("\n📤  Uploading main video ...")
        vid = upload_to_youtube(video_path=video, thumbnail_path=thumb,
            title=meta["title"], description=meta["description"],
            tags=meta["tags"], credentials_json=YOUTUBE_CREDENTIALS)
        print(f"  → https://youtu.be/{vid}")

        print("\n📱  Uploading Short ...")
        short_id = upload_to_youtube(video_path=short_video, thumbnail_path=thumb,
            title=short_meta["title"], description=short_meta["description"],
            tags=short_meta["tags"], credentials_json=YOUTUBE_CREDENTIALS)
        print(f"  → https://youtu.be/{short_id}")

        print(f"\n🎉  Both live! Main: https://youtu.be/{vid} | Short: https://youtu.be/{short_id}")
        return vid

if __name__ == "__main__":
    run()
