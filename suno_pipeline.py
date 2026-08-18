#!/usr/bin/env python3
"""
suno_pipeline.py — Weekly Romantic Song Video + Short
Default: uses ACE-Step generated audio (if available), then saved songs, then instrumental.
"""
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime
import numpy as np
import scipy.io.wavfile as wavfile

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

def generate_instrumental(duration):
    """
    Generate a pleasant instrumental chord progression (not a beep).
    """
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Chord progression: C - G - Am - F
    chords = [
        [261.63, 329.63, 392.00],  # C major
        [392.00, 493.88, 587.33],  # G major
        [220.00, 261.63, 329.63],  # A minor
        [349.23, 440.00, 523.25],  # F major
    ]
    
    chord_duration = 4.0
    audio = np.zeros_like(t)
    for i, chord in enumerate(chords):
        start = i * chord_duration
        end = min((i + 1) * chord_duration, duration)
        if start >= duration:
            break
        mask = (t >= start) & (t < end)
        for freq in chord:
            audio[mask] += 0.3 * np.sin(2 * np.pi * freq * t[mask])
    
    # Simple melody
    melody_notes = [261.63, 293.66, 329.63, 392.00, 440.00, 392.00, 329.63, 261.63]
    melody_duration = 0.5
    for i, note in enumerate(melody_notes):
        start = i * melody_duration + 2.0
        if start >= duration:
            break
        end = min(start + melody_duration, duration)
        mask = (t >= start) & (t < end)
        env = np.sin(np.pi * (t[mask] - start) / melody_duration)
        audio[mask] += 0.15 * env * np.sin(2 * np.pi * note * t[mask])
    
    audio = audio / np.max(np.abs(audio)) * 0.6
    
    fade_len = min(int(sample_rate * 3), len(audio))
    audio[:fade_len] *= np.linspace(0, 1, fade_len)
    audio[-fade_len:] *= np.linspace(1, 0, fade_len)
    
    audio_int16 = (audio * 32767).astype(np.int16)
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wavfile.write(f.name, sample_rate, audio_int16)
        wav_path = f.name
    
    mp3_path = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
    subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_path],
        check=True, capture_output=True
    )
    with open(mp3_path, "rb") as f:
        audio_bytes = f.read()
    
    os.unlink(wav_path)
    os.unlink(mp3_path)
    return audio_bytes

def get_saved_song():
    """Check songs/ folder for MP3 files; use the one matching current week."""
    songs = sorted(SONGS_DIR.glob("*.mp3"))
    if not songs:
        return None, None
    idx = datetime.utcnow().timetuple().tm_yday % len(songs)
    s = songs[idx]
    return str(s), s.stem.replace("_", " ").replace("-", " ").title()

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

def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN", "")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")
    ACESTEP_AUDIO       = os.environ.get("ACESTEP_AUDIO", "")

    if not HF_TOKEN:
        raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS:
        raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

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

        # --- Determine which audio to use ---
        audio_source = None
        # 1. Check for ACE-Step generated audio
        if ACESTEP_AUDIO and os.path.exists(ACESTEP_AUDIO):
            audio_source = ACESTEP_AUDIO
            print(f"🎵  Using ACE-Step generated song: {audio_source}")
        else:
            # 2. Check saved songs folder
            saved_path, saved_title = get_saved_song()
            if saved_path:
                audio_source = saved_path
                title = saved_title
                print(f"🎵  Using saved song: {title}")
            else:
                print("🎵  No external song found. Generating instrumental...")

        if audio_source:
            song_mp3 = audio_source
            # We might need to loop it later if it's shorter than DURATION
        else:
            # Generate instrumental and save as MP3
            audio_data = generate_instrumental(DURATION)
            song_mp3 = str(tmp / "generated_song.mp3")
            with open(song_mp3, "wb") as f:
                f.write(audio_data)
            print(f"  → Instrumental generated: '{title}' ✓")

        # Loop if needed to reach DURATION
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
