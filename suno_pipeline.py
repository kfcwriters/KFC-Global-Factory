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
BASE_URL = "https://acem-api.acemusic.ai"

def get_ace_token():
    """
    Try multiple authentication methods to get a session token.
    """
    url = f"{BASE_URL}/api/acem/user/ai/token"
    
    # Different authentication methods to try
    auth_methods = [
        # Method 1: Bearer token (what we tried, but maybe the key itself is the token)
        {"headers": {"Authorization": f"Bearer {ACE_MUSIC_API_KEY}"}},
        # Method 2: API key as query parameter
        {"params": {"api_key": ACE_MUSIC_API_KEY}},
        # Method 3: API key as header X-API-Key
        {"headers": {"X-API-Key": ACE_MUSIC_API_KEY}},
        # Method 4: API key as header Api-Key
        {"headers": {"Api-Key": ACE_MUSIC_API_KEY}},
        # Method 5: API key in JSON body (POST)
        {"json": {"api_key": ACE_MUSIC_API_KEY}},
        # Method 6: API key as form data (POST)
        {"data": {"api_key": ACE_MUSIC_API_KEY}},
        # Method 7: Bearer token with the token from the playground? Not possible, but we'll try empty
    ]
    
    # Try GET first, then POST
    for method in ["GET", "POST"]:
        for auth in auth_methods:
            try:
                print(f"  [ACE] Trying {method} with {list(auth.keys())}...")
                if method == "GET":
                    resp = requests.get(url, **auth, timeout=30)
                else:
                    # For POST, we need to set content-type appropriately
                    if "json" in auth:
                        resp = requests.post(url, json=auth["json"], timeout=30)
                    elif "data" in auth:
                        resp = requests.post(url, data=auth["data"], timeout=30)
                    else:
                        # If no body, just send with headers
                        headers = auth.get("headers", {})
                        resp = requests.post(url, headers=headers, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    token = data.get("token") or data.get("data", {}).get("token")
                    if token:
                        print(f"  [ACE] Token obtained with {method} {list(auth.keys())}")
                        return token
                    else:
                        print(f"  [ACE] No token in response: {data}")
                else:
                    print(f"  [ACE] {method} with {list(auth.keys())} -> {resp.status_code}")
            except Exception as e:
                print(f"  [ACE] Error: {e}")
    
    # If we reach here, we failed
    raise Exception("Could not obtain session token with any method. Please check your API key.")

def generate_music_with_ace(prompt, lyrics="", duration=30, instrumental=False, language="en"):
    """
    Generate music using ACE Music's API.
    """
    if not ACE_MUSIC_API_KEY:
        raise EnvironmentError("ACE_MUSIC_API_KEY environment variable not set.")
    
    print("  [ACE] Getting session token...")
    session_token = get_ace_token()
    print(f"  [ACE] Using token: {session_token[:10]}...")
    
    # Prepare multipart form data
    data = {
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
        "token": session_token,
    }
    
    headers = {
        "Authorization": f"Bearer {ACE_MUSIC_API_KEY}",  # Keep for release_task
    }
    # Remove Content-Type header for multipart/form-data
    # requests will set it automatically
    
    print("  [ACE] Submitting generation task...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/acem/engine/release_task",
            data=data,
            headers=headers,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Task submission failed: {response.status_code} - {response.text}")
        
        result = response.json()
        task_id = result.get("task_id") or result.get("id")
        
        if not task_id:
            audio_base64 = result.get("audio")
            if audio_base64:
                return base64.b64decode(audio_base64)
            raise Exception(f"No task_id or audio in response: {result}")
        
        print(f"  [ACE] Task submitted. Task ID: {task_id}")
        
        return poll_for_audio_ace(task_id, headers)
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {e}")

def poll_for_audio_ace(task_id, headers):
    """
    Poll the ACE Music API for task completion.
    """
    max_attempts = 60
    for attempt in range(max_attempts):
        try:
            status_response = requests.get(
                f"{BASE_URL}/api/acem/engine/status",
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
                    f"{BASE_URL}/api/acem/engine/query_result",
                    params={"task_id": task_id},
                    headers=headers,
                    timeout=30
                )
                
                if result_response.status_code != 200:
                    raise Exception(f"Failed to fetch result: {result_response.status_code}")
                
                result_data = result_response.json()
                
                audio_base64 = result_data.get("audio")
                if audio_base64:
                    return base64.b64decode(audio_base64)
                
                audio_url = result_data.get("audio_url")
                if audio_url:
                    audio_response = requests.get(audio_url, timeout=60)
                    if audio_response.status_code == 200:
                        return audio_response.content
                
                data_field = result_data.get("data", {})
                audio_base64 = data_field.get("audio")
                if audio_base64:
                    return base64.b64decode(audio_base64)
                
                raise Exception("No audio data found in result")
                
            elif status == "failed" or status == "error":
                error_msg = status_data.get("error", "Unknown error")
                raise Exception(f"Generation failed: {error_msg}")
            
            else:
                progress = status_data.get("progress", "unknown")
                print(f"  [ACE] Status: {status} (progress: {progress}) - waiting...")
                time.sleep(5)
                
        except requests.exceptions.RequestException as e:
            print(f"  [ACE] Polling error (attempt {attempt+1}): {e}")
            time.sleep(5)
            continue
    
    raise Exception(f"Polling timeout after {max_attempts} attempts")

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
