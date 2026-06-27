#!/usr/bin/env python3
"""
pipeline.py — AI Music YouTube Pipeline
========================================
Orchestrates the full daily workflow:
  1. Pick today's niche from config/niches.json
  2. Generate music  (HuggingFace MusicGen API)
  3. Generate images (HuggingFace SDXL API)
  4. Generate metadata (Claude API or template)
  5. Create thumbnail (Pillow)
  6. Assemble video (FFmpeg)
  7. Upload to YouTube (YouTube Data API v3)

Run manually:
    python pipeline.py               # full upload
    python pipeline.py --test        # generate only, skip upload, save to ./output/
    python pipeline.py --niche 2     # override niche index (0-based)
"""

import argparse
import json
import os
import random
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# ── Module imports ───────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent / "src"))

from music_gen      import generate_music
from image_gen      import generate_images
from video_assembly import create_video
from metadata_gen   import generate_metadata
from thumbnail_gen  import create_thumbnail
from youtube_upload import upload_to_youtube


# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────

ROOT      = Path(__file__).parent
CFG_PATH  = ROOT / "config" / "niches.json"
OUT_DIR   = ROOT / "output"


def load_niches() -> list[dict]:
    with open(CFG_PATH, encoding="utf-8") as f:
        return json.load(f)["niches"]


def pick_niche(niches: list[dict], override: int | None = None) -> dict:
    """Rotate through niches by day-of-year, or use override index."""
    if override is not None:
        return niches[override % len(niches)]
    day_index = random.randint(0, len(niches) - 1)
    return niches[day_index]


# ─────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────

def run(test_mode: bool = False, niche_override: int | None = None) -> str | None:
    # ── Environment variables ────────────────────────────────────────────────
    HF_TOKEN             = os.environ.get("HF_TOKEN", "")
    ANTHROPIC_API_KEY    = os.environ.get("ANTHROPIC_API_KEY")   # optional
    YOUTUBE_CREDENTIALS  = os.environ.get("YOUTUBE_CREDENTIALS") # required unless test

    if not HF_TOKEN:
        raise EnvironmentError("HF_TOKEN is not set. "
                               "Get a free token at https://huggingface.co/settings/tokens")
    if not test_mode and not YOUTUBE_CREDENTIALS:
        raise EnvironmentError("YOUTUBE_CREDENTIALS is not set. "
                               "Run setup_youtube_auth.py first.")

    # ── Select niche ─────────────────────────────────────────────────────────
    niches = load_niches()
    niche  = pick_niche(niches, niche_override)

    music_prompt  = random.choice(niche["music_prompts"])
    image_prompts = random.sample(
        niche["image_prompts"],
        min(8, len(niche["image_prompts"]))
    )

    print(f"\n{'='*60}")
    print(f"  Niche       : {niche['name']}")
    print(f"  Music       : {music_prompt}")
    print(f"  Images      : {len(image_prompts)} prompts")
    print(f"  Test mode   : {test_mode}")
    print(f"{'='*60}\n")

    # ── Working directory ─────────────────────────────────────────────────────
    # Use persistent ./output/ in test mode; temp dir for real runs
    if test_mode:
        OUT_DIR.mkdir(exist_ok=True)
        workdir    = OUT_DIR
        cleanup_fn = lambda: None
    else:
        _tmpdir    = tempfile.mkdtemp(prefix="ai_music_")
        workdir    = Path(_tmpdir)
        import shutil
        cleanup_fn = lambda: shutil.rmtree(_tmpdir, ignore_errors=True)

    try:
        # ── Step 1: Music ─────────────────────────────────────────────────────
        print("🎵  Step 1/6 — Generating music …")
        audio_bytes = generate_music(music_prompt, HF_TOKEN, duration_sec=45)
        raw_audio   = workdir / "song_raw.audio"
        raw_audio.write_bytes(audio_bytes)

        # Convert to MP3 for universal compatibility
        mp3_path = workdir / "song.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(raw_audio),
             "-codec:a", "libmp3lame", "-qscale:a", "2", str(mp3_path)],
            check=True, capture_output=True
        )
        print(f"  → {mp3_path} ({mp3_path.stat().st_size // 1024} KB)")

        # ── Step 2: Images ────────────────────────────────────────────────────
        print("\n🖼️   Step 2/6 — Generating images …")
        image_bytes_list = generate_images(image_prompts, HF_TOKEN, vertical=True)

        image_paths = []
        for i, img_bytes in enumerate(image_bytes_list):
            p = workdir / f"image_{i:02d}.jpg"
            p.write_bytes(img_bytes)
            image_paths.append(str(p))

        print(f"  → {len(image_paths)} images saved")

        # ── Step 3: Metadata ──────────────────────────────────────────────────
        print("\n📝  Step 3/6 — Generating metadata …")
        meta = generate_metadata(music_prompt, niche["name"], ANTHROPIC_API_KEY)
        print(f"  → Title: {meta['title']}")

        # ── Step 4: Thumbnail ─────────────────────────────────────────────────
        print("\n🖼️   Step 4/6 — Creating thumbnail …")
        thumb_path = str(workdir / "thumbnail.jpg")
        create_thumbnail(image_bytes_list[0], meta["title"], thumb_path)

        # ── Step 5: Video ─────────────────────────────────────────────────────
        print("\n🎬  Step 5/6 — Assembling video …")
        video_path = str(workdir / "output.mp4")
        create_video(str(mp3_path), image_paths, video_path, vertical=True)

        # ── Step 6: Upload (or save) ──────────────────────────────────────────
        if test_mode:
            print(f"\n✅  Test mode — files saved to {workdir}")
            print(f"     Video     : {video_path}")
            print(f"     Thumbnail : {thumb_path}")
            return video_path

        print("\n📤  Step 6/6 — Uploading to YouTube …")
        video_id = upload_to_youtube(
            video_path       = video_path,
            thumbnail_path   = thumb_path,
            title            = meta["title"],
            description      = meta["description"],
            tags             = meta["tags"],
            credentials_json = YOUTUBE_CREDENTIALS,
        )
        print(f"\n🎉  Done! https://youtu.be/{video_id}")
        return video_id

    finally:
        cleanup_fn()


# ─────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Music YouTube Pipeline")
    parser.add_argument("--test", action="store_true",
                        help="Generate files locally without uploading")
    parser.add_argument("--niche", type=int, default=None,
                        help="Override niche index (0-based)")
    args = parser.parse_args()

    run(test_mode=args.test, niche_override=args.niche)
