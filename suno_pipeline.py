#!/usr/bin/env python3
"""
suno_pipeline.py — Weekly Romantic Song Video + Short
FULLY AUTOMATED — uses ACE Music API (free, no GPU) to generate the full song.
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

# --- ACE Music API Configuration ---
ACE_MUSIC_API_KEY = os.environ.get("ACE_MUSIC_API_KEY")
BASE_URL = "https://ai-api.acemusic.ai"  # The correct base domain

def get_ace_token(headers):
    """
    Try to get a session token from the likely token endpoint.
    """
    # Possible token endpoints on the same domain
    endpoints = [
        f"{BASE_URL}/engine/api/engine/token",
        f"{BASE_URL}/engine/api/token",
        f"{BASE_URL}/api/token",
        f"{BASE_URL}/token",
        f"{BASE_URL}/engine/token",
    ]
    for method in ["GET", "POST"]:
        for url in endpoints:
            try:
                print(f"  [ACE] Trying {method} {url} ...")
                if method == "GET":
                    resp = requests.get(url, headers=headers, timeout=30)
                else:
                    resp = requests.post(url, headers=headers, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    token = data.get("token") or data.get("data", {}).get("token")
                    if token:
                        print(f"  [ACE] Token obtained from {url}")
                        return token
                    else:
                        print(f"  [ACE] No token in response: {data}")
                else:
                    print(f"  [ACE] {url} -> {resp.status_code}")
            except Exception as e:
                print(f"  [ACE] Error with {url}: {e}")
    return None

def generate_music_with_ace(prompt, lyrics="", duration=30, instrumental=False, language="en"):
    """
    Generate music using ACE Music API.
    Tries multiple ways to authenticate and submit the task.
    """
    if not ACE_MUSIC_API_KEY:
        raise EnvironmentError("ACE_MUSIC_API_KEY environment variable not set.")
    
    headers = {
        "Authorization": f"Bearer {ACE_MUSIC_API_KEY}",
        "Origin": "https://acemusic.ai",
        "Referer": "https://acemusic.ai/",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    print("  [ACE] Attempting to get session token...")
    token = get_ace_token(headers)
    if token:
        print(f"  [ACE] Using token: {token[:10]}...")
    else:
        print("  [ACE] No session token obtained. Will try without token field.")
    
    # Prepare base data (same as browser playground)
    base_data = {
        "task_type": "generate",
        "model_type": "acestep-v15-xl-turbo",
        "prompt": prompt,
        "lyrics": lyrics,
        "duration": str(duration),
        "instrumental": "true" if instrumental else "false",
        "vocal_language": language,
        "thinking": "true",
        "audio_format": "mp3",
        "mode": "simple",
    }
    
    # We'll try different combinations of token inclusion
    attempts = []
    
    # If we have a token, try including it in the data
    if token:
        data_with_token = base_data.copy()
        data_with_token["token"] = token
        attempts.append(("with token field", data_with_token, headers.copy()))
    
    # Also try without token field (maybe the Bearer token is enough)
    attempts.append(("without token field", base_data.copy(), headers.copy()))
    
    # Also try with the API key as token (fallback)
    data_with_apikey = base_data.copy()
    data_with_apikey["token"] = ACE_MUSIC_API_KEY
    attempts.append(("with API key as token", data_with_apikey, headers.copy()))
    
    # Try with token in header instead of data
    if token:
        alt_headers = headers.copy()
        alt_headers["X-Token"] = token
        attempts.append(("X-Token header", base_data.copy(), alt_headers))
    
    # Now iterate attempts
    for desc, data, req_headers in attempts:
        # Remove Content-Type header for multipart/form-data (requests will set it)
        req_headers.pop("Content-Type", None)
        print(f"  [ACE] Trying submission: {desc}")
        try:
            resp = requests.post(
                f"{BASE_URL}/engine/api/engine/release_task",
                data=data,
                headers=req_headers,
                timeout=60
            )
            if resp.status_code == 200:
                result = resp.json()
                task_id = result.get("task_id") or result.get("id")
                if task_id:
                    print(f"  [ACE] Task submitted successfully! Task ID: {task_id}")
                    return poll_for_audio_ace(task_id, headers)
                else:
                    # Maybe audio is returned directly
                    audio_b64 = result.get("audio")
                    if audio_b64:
                        return base64.b64decode(audio_b64)
                    print(f"  [ACE] No task_id in response: {result}")
                    continue
            else:
                print(f"  [ACE] Submission failed: {resp.status_code} - {resp.text[:200]}")
        except Exception as e:
            print(f"  [ACE] Request error: {e}")
        time.sleep(1)  # brief pause between attempts
    
    raise Exception("All submission attempts failed. Please check your API key and endpoint.")

def poll_for_audio_ace(task_id, headers):
    """
    Poll for task completion.
    """
    max_attempts = 60
    for attempt in range(max_attempts):
        try:
            status_response = requests.get(
                f"{BASE_URL}/engine/api/engine/status",
                params={"task_id": task_id},
                headers=headers,
                timeout=30
            )
            if status_response.status_code != 200:
                print(f"  [ACE] Status check failed (attempt {attempt+1})")
                time.sleep(5)
                continue
            
            status_data = status_response.json()
            status = status_data.get("status")
            if status == "succeeded" or status == "completed":
                print("  [ACE] Generation complete!")
                result_response = requests.get(
                    f"{BASE_URL}/engine/api/engine/query_result",
                    params={"task_id": task_id},
                    headers=headers,
                    timeout=30
                )
                if result_response.status_code != 200:
                    raise Exception(f"Result fetch failed: {result_response.status_code}")
                result_data = result_response.json()
                audio_b64 = result_data.get("audio") or result_data.get("data", {}).get("audio")
                if audio_b64:
                    return base64.b64decode(audio_b64)
                audio_url = result_data.get("audio_url") or result_data.get("data", {}).get("audio_url")
                if audio_url:
                    audio_resp = requests.get(audio_url, timeout=60)
                    if audio_resp.status_code == 200:
                        return audio_resp.content
                raise Exception("No audio found in result")
            elif status == "failed" or status == "error":
                error_msg = status_data.get("error", "Unknown error")
                raise Exception(f"Generation failed: {error_msg}")
            else:
                progress = status_data.get("progress", "unknown")
                print(f"  [ACE] Status: {status} (progress: {progress}) - waiting...")
                time.sleep(5)
        except Exception as e:
            print(f"  [ACE] Polling error: {e}")
            time.sleep(5)
    raise Exception("Polling timeout")

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
    ACE_MUSIC_API_KEY   = os.environ.get("ACE_MUSIC_API_KEY")

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
