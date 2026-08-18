#!/usr/bin/env python3
"""
suno_pipeline.py — Weekly Romantic Song Video + Short
Uses MiniMax Music 2.6 API (100 free calls/day).
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
import re

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

# ============================================================
# MINIMAX MUSIC 2.6 INTEGRATION
# ============================================================
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY")

def generate_song_minimax(prompt, lyrics="", duration=30):
    """
    Generate music using MiniMax Music 2.6 API.
    Prints full response for debugging.
    Tries both .io and .com endpoints.
    """
    if not MINIMAX_API_KEY:
        raise EnvironmentError("MINIMAX_API_KEY not set")
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "music-2.6",
        "prompt": prompt,
        "lyrics": lyrics,
        "audio_setting": {
            "sample_rate": 44100,
            "bitrate": 256000,
            "format": "mp3"
        }
    }
    
    # Try both endpoints
    endpoints = [
        "https://api.minimax.io/v1/music_generation",
        "https://api.minimaxi.com/v1/music_generation"
    ]
    
    for endpoint in endpoints:
        print(f"  [MiniMax] Trying endpoint: {endpoint}")
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=120)
        except Exception as e:
            print(f"  [MiniMax] Request failed: {e}")
            continue
        
        print(f"  [MiniMax] Status: {response.status_code}")
        if response.status_code != 200:
            print(f"  [MiniMax] Error response: {response.text[:500]}")
            continue
        
        try:
            data = response.json()
        except Exception as e:
            print(f"  [MiniMax] Failed to parse JSON: {e}")
            continue
        
        # Print full JSON for debugging
        print(f"  [MiniMax] Response JSON: {json.dumps(data, indent=2)[:1500]}")
        
        # Try multiple ways to extract audio
        audio_hex = None
        
        # 1: data.data.audio
        if data.get("data") and isinstance(data["data"], dict):
            audio_hex = data["data"].get("audio")
        
        # 2: data.audio
        if not audio_hex and data.get("audio"):
            audio_hex = data.get("audio")
        
        # 3: data.result.audio
        if not audio_hex and data.get("result") and isinstance(data["result"], dict):
            audio_hex = data["result"].get("audio")
        
        # 4: data.output.audio
        if not audio_hex and data.get("output") and isinstance(data["output"], dict):
            audio_hex = data["output"].get("audio")
        
        # 5: data.audio_url (if they give a URL instead)
        audio_url = None
        if data.get("data") and isinstance(data["data"], dict):
            audio_url = data["data"].get("audio_url")
        if not audio_url and data.get("audio_url"):
            audio_url = data.get("audio_url")
        
        if audio_hex:
            print("  [MiniMax] Audio extracted as hex")
            return bytes.fromhex(audio_hex)
        elif audio_url:
            print(f"  [MiniMax] Downloading audio from URL: {audio_url}")
            audio_resp = requests.get(audio_url, timeout=60)
            if audio_resp.status_code == 200:
                return audio_resp.content
            else:
                print(f"  [MiniMax] Failed to download from URL: {audio_resp.status_code}")
        else:
            print("  [MiniMax] No audio found in response")
    
    raise Exception("All endpoints failed or no audio in response")

# ============================================================
# FALLBACK: Procedural tone
# ============================================================
def generate_procedural_tone(duration):
    """Generate a soft chord as placeholder."""
    import numpy as np
    import scipy.io.wavfile as wavfile
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    freqs = [440, 554, 659]
    audio = np.zeros_like(t)
    for freq in freqs:
        audio += 0.3 * np.sin(2 * np.pi * freq * t)
    audio = audio / np.max(np.abs(audio)) * 0.5
    buf = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wavfile.write(buf.name, sample_rate, (audio * 32767).astype(np.int16))
    with open(buf.name, "rb") as f:
        audio_bytes = f.read()
    os.unlink(buf.name)
    return audio_bytes

# ============================================================
# MAIN GENERATE FUNCTION
# ============================================================
def generate_song(prompt, lyrics, title, duration):
    """Try MiniMax, fallback to procedural."""
    try:
        print("  [Music] Attempting MiniMax Music 2.6...")
        return generate_song_minimax(prompt, lyrics, duration)
    except Exception as e:
        print(f"  [Music] MiniMax failed: {e}")
        print("  [Music] Generating procedural tone...")
        return generate_procedural_tone(duration)

# ============================================================
# Helper functions (unchanged)
# ============================================================
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

# ============================================================
# MAIN PIPELINE
# ============================================================
def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN", "")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")
    MINIMAX_API_KEY     = os.environ.get("MINIMAX_API_KEY")

    if not HF_TOKEN:
        raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS:
        raise EnvironmentError("YOUTUBE_CREDENTIALS not set")
    if not MINIMAX_API_KEY:
        raise EnvironmentError("MINIMAX_API_KEY not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline : Romantic Song Video + Short (Weekly, Fully Automated)")
    print(f"{'='*60}\n")

    with tempfile.TemporaryDirectory(prefix="romantic_") as tmp:
        tmp = Path(tmp)

        song = generate_weekly_lyrics()
        title = song["title"]
        style_used = song.get("style", "romantic pop, female vocal, emotional")
        sections = song.get("sections") or [
            {"type": "verse",  "lines": song["prompt"].split("\n")[:4]},
            {"type": "chorus", "lines": song["prompt"].split("\n")[4:8]},
        ]

        saved, saved_title = get_saved_song()
        if saved:
            song_mp3 = saved
            title = saved_title
            print(f"🎵  Using saved song: {title}")
        else:
            print("🎵  Generating song with MiniMax Music 2.6...")
            mood = detect_mood(style_used)
            music_prompt = f"{style_used}, {mood} mood"
            full_lyrics = "\n".join(["\n".join(sec.get("lines", [])) for sec in sections])

            audio_data = generate_song(
                prompt=music_prompt,
                lyrics=full_lyrics,
                title=title,
                duration=DURATION
            )

            song_mp3 = str(tmp / "generated_song.mp3")
            with open(song_mp3, "wb") as f:
                f.write(audio_data)

            print(f"  → Song generated: '{title}' ✓")

        dur = probe_duration(song_mp3)
        if dur < DURATION - 10:
            looped = str(tmp / "looped.mp3")
            subprocess.run(["ffmpeg","-y","-stream_loop","-1","-i",song_mp3,
                           "-t",str(DURATION),"-c","copy",looped],
                          check=True, capture_output=True)
            song_mp3 = looped
        dur = min(dur, DURATION)
        n_images = min(16, max(8, int(dur / 15)))

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
