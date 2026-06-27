#!/usr/bin/env python3
"""
romantic_pipeline.py
====================
Dedicated pipeline for romantic songs — 3+ minutes long.
Runs SEPARATELY from the main pipeline (different workflow, different schedule).
Uses the same src/ modules — zero duplication.

Schedule : Daily at 2:00 PM UTC (7:30 PM IST) — prime evening time for romantic music
Duration : 210 seconds (3 min 30 sec)
Images   : 16 romantic couple scenes
"""

import json
import os
import random
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from music_gen      import generate_music
from image_gen      import generate_images
from video_assembly import create_video
from metadata_gen   import generate_metadata
from thumbnail_gen  import create_thumbnail
from youtube_upload import upload_to_youtube

# ── Config ────────────────────────────────────────────────────────────────────
ROOT           = Path(__file__).parent
CFG_PATH       = ROOT / "config" / "romantic_config.json"
DURATION_SEC   = 210      # 3 min 30 sec
NUM_IMAGES     = 16       # more images = more variety for longer video


def load_config() -> dict:
    with open(CFG_PATH, encoding="utf-8") as f:
        return json.load(f)["niches"][0]


def run():
    # ── Env ───────────────────────────────────────────────────────────────────
    HF_TOKEN            = os.environ.get("HF_TOKEN", "")
    ANTHROPIC_API_KEY   = os.environ.get("ANTHROPIC_API_KEY")
    YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS")

    if not HF_TOKEN:
        raise EnvironmentError("HF_TOKEN not set")
    if not YOUTUBE_CREDENTIALS:
        raise EnvironmentError("YOUTUBE_CREDENTIALS not set")

    # ── Load romantic config ──────────────────────────────────────────────────
    niche         = load_config()
    music_prompt  = random.choice(niche["music_prompts"])
    # Pick 16 random image prompts (with replacement if needed)
    all_prompts   = niche["image_prompts"]
    image_prompts = [random.choice(all_prompts) for _ in range(NUM_IMAGES)]

    print(f"\n{'='*60}")
    print(f"  Pipeline     : Romantic Songs")
    print(f"  Duration     : {DURATION_SEC}s ({DURATION_SEC//60}m {DURATION_SEC%60}s)")
    print(f"  Images       : {NUM_IMAGES}")
    print(f"  Music prompt : {music_prompt}")
    print(f"{'='*60}\n")

    with tempfile.TemporaryDirectory(prefix="romantic_") as tmpdir:
        tmpdir = Path(tmpdir)

        # ── Step 1: Music ────────────────────────────────────────────────────
        print("🎵  Step 1/6 — Generating romantic music …")
        audio_bytes = generate_music(music_prompt, HF_TOKEN,
                                     duration_sec=DURATION_SEC)
        raw_audio   = tmpdir / "song_raw.audio"
        raw_audio.write_bytes(audio_bytes)

        mp3_path = tmpdir / "song.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(raw_audio),
             "-codec:a", "libmp3lame", "-qscale:a", "2", str(mp3_path)],
            check=True, capture_output=True
        )
        print(f"  → {mp3_path.stat().st_size // 1024} KB")

        # ── Step 2: Images ───────────────────────────────────────────────────
        print(f"\n🖼️   Step 2/6 — Generating {NUM_IMAGES} romantic images …")
        image_bytes_list = generate_images(image_prompts, HF_TOKEN)

        image_paths = []
        for i, img_bytes in enumerate(image_bytes_list):
            p = tmpdir / f"img_{i:02d}.jpg"
            p.write_bytes(img_bytes)
            image_paths.append(str(p))
        print(f"  → {len(image_paths)} images saved")

        # ── Step 3: Metadata ─────────────────────────────────────────────────
        print("\n📝  Step 3/6 — Generating metadata …")
        meta = generate_metadata(
            music_prompt,
            "romantic hindi english songs",
            ANTHROPIC_API_KEY
        )
        print(f"  → Title: {meta['title']}")

        # ── Step 4: Thumbnail ────────────────────────────────────────────────
        print("\n🖼️   Step 4/6 — Creating thumbnail …")
        thumb_path = str(tmpdir / "thumbnail.jpg")
        create_thumbnail(image_bytes_list[0], meta["title"], thumb_path)

        # ── Step 5: Video ────────────────────────────────────────────────────
        print("\n🎬  Step 5/6 — Assembling video …")
        video_path = str(tmpdir / "romantic_output.mp4")
        create_video(str(mp3_path), image_paths, video_path)

        # ── Step 6: Upload ───────────────────────────────────────────────────
        print("\n📤  Step 6/6 — Uploading to YouTube …")
        video_id = upload_to_youtube(
            video_path        = video_path,
            thumbnail_path    = thumb_path,
            title             = meta["title"],
            description       = meta["description"],
            tags              = meta["tags"],
            credentials_json  = YOUTUBE_CREDENTIALS,
        )

        print(f"\n🎉  Romantic song live! https://youtu.be/{video_id}")
        return video_id


if __name__ == "__main__":
    run()
