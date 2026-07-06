"""
Main orchestrator: picks a niche, generates music + images + metadata
+ thumbnail, assembles the video, and (unless --test) uploads it.

Usage:
  python pipeline.py               # full run + upload, niche picked by day
  python pipeline.py --test        # generate only, save to ./output/, no upload
  python pipeline.py --niche 3     # force a specific niche index
"""
import os
import sys
import json
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from music_gen import generate_music
from image_gen import generate_image
from metadata_gen import generate_metadata
from thumbnail_gen import generate_thumbnail
from video_assembly import assemble_video
from youtube_upload import upload_video

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "ai_music_output")
NICHES_PATH = os.path.join(os.path.dirname(__file__), "config", "music_niches.json")


def load_niches():
    with open(NICHES_PATH) as f:
        return json.load(f)["niches"]


def pick_niche(niches, forced_index=None):
    if forced_index is not None:
        return niches[forced_index % len(niches)]
    day_index = datetime.datetime.utcnow().timetuple().tm_yday
    return niches[day_index % len(niches)]


def run(test_mode: bool = False, forced_index: int = None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    niches = load_niches()
    niche = pick_niche(niches, forced_index)
    print(f"=== Niche: {niche['name']} ===")

    print("\n[1/5] Generating music...")
    music_path = os.path.join(OUTPUT_DIR, "music.wav")
    generate_music(niche["music_prompts"][0], music_path)

    print("\n[2/5] Generating images...")
    image_paths = []
    for i, prompt in enumerate(niche["image_prompts"]):
        img_path = os.path.join(OUTPUT_DIR, f"image_{i}.png")
        generate_image(prompt, img_path)
        image_paths.append(img_path)

    print("\n[3/5] Generating metadata...")
    metadata = generate_metadata(niche["name"])
    print(f"  Title: {metadata['title']}")

    print("\n[4/5] Generating thumbnail...")
    thumbnail_path = os.path.join(OUTPUT_DIR, "thumbnail.jpg")
    generate_thumbnail(image_paths[0], metadata["title"], thumbnail_path)

    print("\n[5/5] Assembling video...")
    final_path = os.path.join(OUTPUT_DIR, "final_video.mp4")
    assemble_video(image_paths, music_path, final_path)

    if test_mode:
        print(f"\nTest mode: skipping upload. Files are in {OUTPUT_DIR}/")
        return

    print("\nUploading to YouTube...")
    upload_video(
        video_path=final_path,
        title=metadata["title"],
        description=metadata["description"],
        tags=metadata["tags"],
        thumbnail_path=thumbnail_path,
        privacy="public",
        made_for_kids=False,
    )


if __name__ == "__main__":
    test_mode = "--test" in sys.argv
    forced_index = None
    if "--niche" in sys.argv:
        idx = sys.argv.index("--niche")
        forced_index = int(sys.argv[idx + 1])
    run(test_mode=test_mode, forced_index=forced_index)
