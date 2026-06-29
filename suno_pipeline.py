#!/usr/bin/env python3
"""
suno_pipeline.py
================
Fully automated romantic song lyric video pipeline.

If SUNO_COOKIE is set → generates a FRESH Suno AI song every day automatically.
If SUNO_COOKIE is not set → picks from saved songs/ folder (manual fallback).

Schedule: Daily at 11:00 PM IST
"""
import os, random, subprocess, sys, tempfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))
from suno_gen       import generate_suno_song
from image_gen      import generate_images
from lyrics_overlay import add_lyrics
from video_assembly import create_video
from metadata_gen   import generate_metadata
from thumbnail_gen  import create_thumbnail
from youtube_upload import upload_to_youtube

SONGS_DIR = Path(__file__).parent / "songs"

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
    "couple on swing at sunrise, soft morning mist, peaceful love",
    "man holding woman from behind watching sunset over ocean together",
]


def probe_duration(path: str) -> float:
    r = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    return float(r.stdout.strip() or 180)


def pick_saved_song() -> Path:
    """Fallback: pick a song from songs/ folder by day rotation."""
    songs = sorted(SONGS_DIR.glob("*.mp3"))
    if not songs:
        raise FileNotFoundError(
            "No songs found! Either set SUNO_COOKIE secret for auto-generation, "
            "or add MP3 files to the songs/ folder."
        )
    idx  = datetime.utcnow().timetuple().tm_yday % len(songs)
    song = songs[idx]
    print(f"  → Saved song: {song.name} ({idx+1}/{len(songs)})")
    return song


def title_from_path(p: Path) -> str:
    return p.stem.replace("_"," ").replace("-"," ").title()


def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN","")
    ANTHROPIC_API_KEY   = os.environ.get("ANTHROPIC_API_KEY")
    SUNO_COOKIE         = os.environ.get("SUNO_COOKIE")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")

    if not HF_TOKEN:            raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS: raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    print(f"\n{'='*60}")
    if SUNO_COOKIE:
        print(f"  Mode     : 🤖 FULLY AUTOMATED (Suno AI generates fresh song)")
    else:
        print(f"  Mode     : 📁 SAVED SONGS (add SUNO_COOKIE for full automation)")
    print(f"{'='*60}\n")

    with tempfile.TemporaryDirectory(prefix="suno_") as tmp:
        tmp = Path(tmp)
        song_mp3  = str(tmp / "song.mp3")
        song_title = "Romantic Song"

        # ── Step 1: Get the song ─────────────────────────────────────────────
        if SUNO_COOKIE:
            print("🎵  Step 1/5 — Generating fresh Suno AI song ...")
            try:
                mp3_bytes, song_title = generate_suno_song(SUNO_COOKIE)
                Path(song_mp3).write_bytes(mp3_bytes)
                print(f"  → Generated: '{song_title}'")
            except Exception as e:
                print(f"  ⚠️  Suno failed ({e})")
                print(f"  → Falling back to saved songs folder ...")
                saved = pick_saved_song()
                song_mp3   = str(saved)
                song_title = title_from_path(saved)
        else:
            print("🎵  Step 1/5 — Loading saved song ...")
            saved      = pick_saved_song()
            song_mp3   = str(saved)
            song_title = title_from_path(saved)

        duration = probe_duration(song_mp3)
        n_images = min(16, max(8, int(duration / 15)))
        print(f"  → Title: {song_title}")
        print(f"  → Duration: {duration:.0f}s  |  Images: {n_images}")

        # ── Step 2: Generate romantic images ─────────────────────────────────
        print(f"\n🖼️   Step 2/5 — Generating {n_images} romantic images ...")
        prompts  = random.sample(BG_PROMPTS, min(n_images, len(BG_PROMPTS)))
        while len(prompts) < n_images:
            prompts.append(random.choice(BG_PROMPTS))
        raw_imgs = generate_images(prompts, HF_TOKEN, vertical=False)

        image_paths = []
        for i, img in enumerate(raw_imgs):
            # Show song title on each frame
            frame = add_lyrics(img, [song_title], "verse", "")
            p = tmp / f"frame_{i:02d}.jpg"
            p.write_bytes(frame)
            image_paths.append(str(p))

        # ── Step 3: Metadata ──────────────────────────────────────────────────
        print("\n📝  Step 3/5 — Generating metadata ...")
        meta = generate_metadata(
            f"romantic love song — {song_title}",
            "romantic songs", ANTHROPIC_API_KEY)
        meta["title"] = f"🎵 {song_title} | Romantic Song 🌹"[:100]
        meta["tags"]  = (["romantic song","love song","suno ai","ai music",
                          "romantic music","love ballad","romantic video",
                          "beautiful love song"] + meta.get("tags",[]))[:15]
        print(f"  → {meta['title']}")

        # Thumbnail
        thumb = str(tmp / "thumbnail.jpg")
        create_thumbnail(raw_imgs[0], meta["title"], thumb)

        # ── Step 4: Assemble video ────────────────────────────────────────────
        print("\n🎬  Step 4/5 — Assembling video ...")
        video_path = str(tmp / "output.mp4")
        create_video(song_mp3, image_paths, video_path, vertical=False)

        # ── Step 5: Upload ────────────────────────────────────────────────────
        print("\n📤  Step 5/5 — Uploading to YouTube ...")
        vid = upload_to_youtube(
            video_path       = video_path,
            thumbnail_path   = thumb,
            title            = meta["title"],
            description      = meta["description"],
            tags             = meta["tags"],
            credentials_json = YOUTUBE_CREDENTIALS,
        )
        print(f"\n🎉  Live! https://youtu.be/{vid}")
        return vid


if __name__ == "__main__":
    run()
