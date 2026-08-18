#!/usr/bin/env python3
"""
suno_pipeline.py — Weekly Romantic Song Video + Short
Primary: Hugging Face Bark (Inference API) – free, reliable with retries
Fallback: ACE Music API (if token available)
Last resort: procedural tone
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
# 1. HUGGING FACE BARK (Primary – free, rate-limited)
# ============================================================
def generate_song_bark(prompt, lyrics="", duration=30):
    """
    Generate singing using Bark via Hugging Face Inference API.
    Free tier: ~1000 requests/day (sufficient for weekly runs).
    """
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise Exception("HF_TOKEN not set")
    
    text = f"♪ ({prompt}) {lyrics} ♪"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": text, "parameters": {"do_sample": True, "temperature": 0.6}}
    
    # Retry with backoff
    for attempt in range(5):
        try:
            resp = requests.post(
                "https://api-inference.huggingface.co/models/suno/bark",
                json=payload,
                headers=headers,
                timeout=120
            )
            if resp.status_code == 200:
                return resp.content  # returns WAV
            elif resp.status_code == 503:
                print(f"  [Bark] Model loading, waiting {10*(attempt+1)}s...")
                time.sleep(10*(attempt+1))
                continue
            else:
                print(f"  [Bark] Attempt {attempt+1} failed: {resp.status_code}")
                time.sleep(3)
        except Exception as e:
            print(f"  [Bark] Attempt {attempt+1} error: {e}")
            time.sleep(5)
    raise Exception("Bark failed after retries")

# ============================================================
# 2. ACE MUSIC API (Fallback – if token is valid)
# ============================================================
def generate_song_ace(prompt, lyrics, duration):
    token = os.environ.get("ACE_SESSION_TOKEN")
    if not token:
        raise Exception("ACE_SESSION_TOKEN not set")
    
    headers = {
        "Origin": "https://acemusic.ai",
        "Referer": "https://acemusic.ai/",
        "Accept": "application/json",
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
        raise Exception(f"ACE submission failed: {resp.status_code}")
    result = resp.json()
    task_id = result.get("task_id")
    if not task_id:
        raise Exception("No task_id")
    for _ in range(30):
        status = requests.get(
            "https://ai-api.acemusic.ai/engine/api/engine/status",
            params={"task_id": task_id},
            headers=headers
        )
        if status.status_code != 200:
            time.sleep(5)
            continue
        status_data = status.json()
        if status_data.get("status") == "succeeded":
            result_resp = requests.get(
                "https://ai-api.acemusic.ai/engine/api/engine/query_result",
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
    raise Exception("ACE generation timed out")

# ============================================================
# 3. PROCEDURAL TONE (Last resort)
# ============================================================
def generate_procedural_tone(duration):
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
    # 1. Try Bark
    try:
        print("  [Music] Attempting Hugging Face Bark...")
        return generate_song_bark(prompt, lyrics, duration)
    except Exception as e:
        print(f"  [Music] Bark failed: {e}")
    
    # 2. Try ACE (if token available)
    try:
        print("  [Music] Attempting ACE Music API...")
        return generate_song_ace(prompt, lyrics, duration)
    except Exception as e:
        print(f"  [Music] ACE failed: {e}")
    
    # 3. Procedural
    print("  [Music] All APIs failed. Generating procedural tone...")
    return generate_procedural_tone(duration)

# ============================================================
# Helper functions (unchanged – keep these)
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

    if not HF_TOKEN:
        raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS:
        raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

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
            print("🎵  Generating song...")
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
