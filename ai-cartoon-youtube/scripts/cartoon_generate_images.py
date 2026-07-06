"""
Step 2: Generate one image per scene using Pollinations.ai
(https://pollinations.ai) — free, no API key required.

It's a simple HTTP GET that returns an image. We use a fixed seed
+ consistent style text (from config.py) to keep the look coherent
across scenes and episodes.
"""
import os
import sys
import json
import time
import urllib.request
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "config"))
from cartoon_config import IMAGE_SEED, VIDEO_WIDTH, VIDEO_HEIGHT

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt/"


def generate_image(prompt: str, seed: int, out_path: str, retries: int = 3):
    encoded_prompt = urllib.parse.quote(prompt)
    url = (
        f"{POLLINATIONS_BASE}{encoded_prompt}"
        f"?width={VIDEO_WIDTH}&height={VIDEO_HEIGHT}&seed={seed}&nologo=true"
    )
    for attempt in range(1, retries + 1):
        try:
            urllib.request.urlretrieve(url, out_path)
            # Basic sanity check: file should be non-trivial size
            if os.path.getsize(out_path) > 5000:
                return
        except Exception as e:
            print(f"  attempt {attempt} failed: {e}")
        time.sleep(3)
    raise RuntimeError(f"Failed to generate image for prompt: {prompt[:60]}...")


def generate_all_images(script_path: str, out_dir: str):
    with open(script_path) as f:
        scenes = json.load(f)

    os.makedirs(out_dir, exist_ok=True)
    for i, scene in enumerate(scenes):
        out_path = os.path.join(out_dir, f"scene_{i:02d}.png")
        print(f"Generating image {i+1}/{len(scenes)}...")
        # Use the same base seed + index so characters stay visually similar
        # scene-to-scene, but each image still differs.
        generate_image(scene["image_prompt"], seed=IMAGE_SEED + i, out_path=out_path)
        scene["image_path"] = out_path

    with open(script_path, "w") as f:
        json.dump(scenes, f, indent=2)

    print(f"All {len(scenes)} images saved to {out_dir}")


if __name__ == "__main__":
    base = os.path.join(os.path.dirname(__file__), "..", "cartoon_output")
    generate_all_images(
        script_path=os.path.join(base, "script.json"),
        out_dir=os.path.join(base, "images"),
    )
