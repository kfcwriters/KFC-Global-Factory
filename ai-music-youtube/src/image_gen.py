"""
Generates a background image from a text prompt using HuggingFace's
free Inference API (stabilityai/stable-diffusion-xl-base-1.0).

Same caveat as music_gen.py: free HF inference can 503 (cold start) or
be rate-limited. Retries with backoff; falls back to a simple generated
gradient image (via Pillow) so the pipeline never hard-fails.
"""
import os
import time
import requests
from PIL import Image, ImageDraw
import random

HF_TOKEN = os.environ.get("HF_TOKEN")
SDXL_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"


def _gradient_fallback(out_path: str, width: int = 1280, height: int = 720):
    """Simple calming gradient image as a last-resort fallback."""
    palettes = [
        ((30, 60, 90), (140, 190, 210)),
        ((40, 30, 60), (170, 140, 200)),
        ((20, 50, 40), (150, 200, 170)),
    ]
    top, bottom = random.choice(palettes)
    img = Image.new("RGB", (width, height), top)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        ratio = y / height
        r = int(top[0] + (bottom[0] - top[0]) * ratio)
        g = int(top[1] + (bottom[1] - top[1]) * ratio)
        b = int(top[2] + (bottom[2] - top[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    img.save(out_path)
    print("  [fallback] Used generated gradient image instead of SDXL.")


def generate_image(prompt: str, out_path: str, width: int = 1280, height: int = 720, retries: int = 6):
    if not HF_TOKEN:
        print("  HF_TOKEN not set — using gradient fallback.")
        _gradient_fallback(out_path, width, height)
        return

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}

    for attempt in range(1, retries + 1):
        resp = requests.post(SDXL_URL, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
            with open(out_path, "wb") as f:
                f.write(resp.content)
            return
        if resp.status_code == 503:
            wait = min(20 * attempt, 90)
            print(f"  SDXL warming up (attempt {attempt}/{retries}), waiting {wait}s...")
            time.sleep(wait)
            continue
        print(f"  SDXL error {resp.status_code}: {resp.text[:200]}")
        time.sleep(5)

    print("  SDXL unavailable after retries — using gradient fallback.")
    _gradient_fallback(out_path, width, height)


if __name__ == "__main__":
    generate_image("peaceful nature scene with morning light", out_path="test_image.png")
