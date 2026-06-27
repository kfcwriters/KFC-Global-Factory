#!/usr/bin/env python3
"""
lyrics_pipeline.py
==================
Pipeline 3 — Hindi + English Romantic Lyric Videos.

What it does:
  1. Generates original bilingual lyrics (Claude API or template)
  2. Creates romantic couple images for each lyric section
  3. Overlays lyrics text on each image (lyric-video style)
  4. Composes romantic instrumental music (3.5 minutes)
  5. Assembles full lyric video
  6. Uploads to YouTube

Schedule : Daily at 11:00 PM IST (5:30 PM UTC)
Duration : 210 seconds (3 min 30 sec)
Format   : Landscape 1280x720
"""

import json, os, random, subprocess, sys, tempfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

from lyrics_gen     import generate_lyrics
from lyrics_overlay import add_lyrics
from image_gen      import generate_images
from music_gen      import generate_music
from video_assembly import create_video
from metadata_gen   import generate_metadata
from thumbnail_gen  import create_thumbnail
from youtube_upload import upload_to_youtube

DURATION_SEC = 210   # 3 min 30 sec

# Romantic couple image prompts for backgrounds
BG_PROMPTS = [
    "romantic couple holding hands at golden sunset on beach, cinematic warm glow",
    "couple slow dancing in candlelit room with rose petals, soft bokeh lights",
    "two lovers on rooftop under stars, city lights below, romantic night",
    "couple under cherry blossom tree, pink petals falling, dreamy spring light",
    "man surprising woman with roses in garden, romantic golden evening",
    "couple sharing umbrella in gentle rain, warm street lights reflection",
    "silhouette of couple embracing at sunset on hill, dramatic orange sky",
    "couple sitting by lake at twilight, fairy lights on water reflection",
    "woman in red dress and man dancing at outdoor wedding, fairy lights everywhere",
    "couple on boat in misty river at dawn, mountains behind them",
    "close up of two hands intertwined, soft bokeh golden background",
    "couple watching stars lying on grass, milky way above, peaceful romantic",
]


def build_lyric_frames(sections: list, hf_token: str, song_title: str) -> list:
    """
    For each section generate one background image and overlay lyrics.
    Returns list of JPEG bytes (one per section).
    """
    n = len(sections)
    # Pick background prompts (cycle if more sections than prompts)
    bg_list   = random.sample(BG_PROMPTS, min(n, len(BG_PROMPTS)))
    while len(bg_list) < n:
        bg_list.append(random.choice(BG_PROMPTS))

    print(f"\n🖼️  Generating {n} lyric frames …")
    raw_images = generate_images(bg_list, hf_token, vertical=False)

    frames = []
    for i, (section, img_bytes) in enumerate(zip(sections, raw_images)):
        lines        = section["lines"][:4]   # max 4 lines per frame
        section_type = section.get("type", "verse")
        frame        = add_lyrics(img_bytes, lines, section_type, song_title)
        frames.append(frame)
        print(f"  [frame {i+1}/{n}] lyrics overlaid ✓")

    return frames


def make_metadata(song: dict, anthropic_api_key: str | None) -> dict:
    """Build YouTube title/description from song info."""
    title  = song.get("title", "Romantic Hindi English Song")
    prompt = f"romantic bilingual Hindi English love song — {title}"

    meta = generate_metadata(prompt, "romantic hindi english songs", anthropic_api_key)

    # Override title with actual song title for lyric videos
    meta["title"] = f"🎵 {title} | Romantic Hindi English Song 🌹"[:100]

    # Enrich description
    section_titles = " | ".join(
        s["type"].upper() for s in song.get("sections", [])
    )
    meta["description"] = (
        f"🎵 {title}\n\n"
        f"Original Hindi + English romantic lyric video.\n\n"
        f"Song structure: {section_titles}\n\n"
        f"{meta.get('description', '')}"
    )[:5000]

    extra_tags = ["hindi songs", "romantic hindi song", "hindi english song",
                  "bollywood romantic", "lyric video", "hindi love song",
                  "hinglish song", "romantic song 2025"]
    meta["tags"] = (extra_tags + meta.get("tags", []))[:15]
    return meta


def run():
    HF_TOKEN            = os.environ.get("HF_TOKEN", "")
    ANTHROPIC_API_KEY   = os.environ.get("ANTHROPIC_API_KEY")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")

    if not HF_TOKEN:
        raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS:
        raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    print(f"\n{'='*60}")
    print(f"  Pipeline     : Hindi+English Lyric Video")
    print(f"  Duration     : {DURATION_SEC}s ({DURATION_SEC//60}m {DURATION_SEC%60}s)")
    print(f"{'='*60}\n")

    # ── Step 1: Generate lyrics ───────────────────────────────────────────
    print("📝  Step 1/6 — Generating lyrics …")
    song     = generate_lyrics(ANTHROPIC_API_KEY)
    sections = song["sections"]
    print(f"  → Song: {song['title']} ({len(sections)} sections)")

    # ── Step 2: Generate lyric frames (images + lyrics overlay) ──────────
    frames = build_lyric_frames(sections, HF_TOKEN, song["title"])

    with tempfile.TemporaryDirectory(prefix="lyrics_") as tmpdir:
        tmpdir = Path(tmpdir)

        # Save frames
        image_paths = []
        for i, frame_bytes in enumerate(frames):
            p = tmpdir / f"frame_{i:02d}.jpg"
            p.write_bytes(frame_bytes)
            image_paths.append(str(p))

        # ── Step 3: Generate music ────────────────────────────────────────
        print("\n🎵  Step 3/6 — Composing romantic music …")
        music_prompt = random.choice([
            "soft romantic piano with gentle strings, slow love ballad, Bollywood style",
            "acoustic guitar with sitar, warm romantic evening, Hindi film music style",
            "smooth violin with piano, passionate love theme, cinematic and slow",
            "soft bansuri flute with tabla, romantic Indian classical fusion, soulful",
        ])
        audio_bytes = generate_music(music_prompt, HF_TOKEN, duration_sec=DURATION_SEC)
        raw_audio   = tmpdir / "song_raw.audio"
        raw_audio.write_bytes(audio_bytes)

        mp3_path = tmpdir / "song.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(raw_audio),
             "-codec:a", "libmp3lame", "-qscale:a", "2", str(mp3_path)],
            check=True, capture_output=True
        )
        print(f"  → {mp3_path.stat().st_size // 1024} KB")

        # ── Step 4: Metadata ──────────────────────────────────────────────
        print("\n📝  Step 4/6 — Generating metadata …")
        meta = make_metadata(song, ANTHROPIC_API_KEY)
        print(f"  → Title: {meta['title']}")

        # ── Step 5: Thumbnail (first frame) ───────────────────────────────
        print("\n🖼️   Step 5/6 — Creating thumbnail …")
        thumb_path = str(tmpdir / "thumbnail.jpg")
        create_thumbnail(frames[0], meta["title"], thumb_path)

        # ── Step 6a: Assemble video ───────────────────────────────────────
        print("\n🎬  Step 6/6 — Assembling lyric video …")
        video_path = str(tmpdir / "lyrics_output.mp4")
        create_video(str(mp3_path), image_paths, video_path, vertical=False)

        # ── Step 6b: Upload ───────────────────────────────────────────────
        print("\n📤  Uploading to YouTube …")
        video_id = upload_to_youtube(
            video_path       = video_path,
            thumbnail_path   = thumb_path,
            title            = meta["title"],
            description      = meta["description"],
            tags             = meta["tags"],
            credentials_json = YOUTUBE_CREDENTIALS,
        )

        print(f"\n🎉  Lyric video live! https://youtu.be/{video_id}")
        return video_id


if __name__ == "__main__":
    run()
