"""
image_gen.py
Generates images via HuggingFace Inference API (SDXL).
Falls back to a Pillow-drawn gradient if the API fails.
"""

import io
import time
import random
import requests
from PIL import Image, ImageDraw


HF_MODEL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
MAX_RETRIES = 4
RETRY_SLEEP  = 35   # seconds

# Visual style modifiers — appended to every prompt for variety
STYLE_TAGS = [
    "cinematic lighting, 4k, atmospheric, ultra detailed",
    "oil painting style, vibrant colors, rich texture, artstation",
    "watercolor art, soft pastel tones, dreamy, ethereal",
    "digital art, neon accent, dramatic shadows, photorealistic",
    "pencil sketch with color wash, artistic, detailed linework",
    "golden hour photography, warm tones, shallow depth of field",
    "moody dark fantasy, deep shadows, mystical atmosphere",
]

# Gradient palette for fallback images
FALLBACK_PALETTES = [
    [(20, 0, 50), (80, 0, 120)],
    [(0, 20, 60), (0, 80, 160)],
    [(40, 10, 0), (140, 60, 0)],
    [(5, 30, 10), (20, 100, 40)],
    [(30, 0, 0), (110, 20, 20)],
]


def generate_images(prompts: list[str], hf_token: str) -> list[bytes]:
    """
    Generate one image per prompt.

    Args:
        prompts  : List of image description strings.
        hf_token : HuggingFace API token.

    Returns:
        List of raw JPEG/PNG bytes (one per prompt).
        Failed slots are replaced with a gradient fallback.
    """
    headers = {"Authorization": f"Bearer {hf_token}"}
    results = []

    for idx, prompt in enumerate(prompts):
        style   = random.choice(STYLE_TAGS)
        full_q  = f"{prompt}, {style}"
        payload = {
            "inputs": full_q,
            "parameters": {"width": 1280, "height": 720}
        }

        success = False
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"  [image {idx + 1}/{len(prompts)}] attempt {attempt} …")
            try:
                resp = requests.post(
                    HF_MODEL, headers=headers, json=payload, timeout=90
                )
            except requests.exceptions.Timeout:
                print("  [image] timeout, retrying …")
                time.sleep(10)
                continue

            if resp.status_code == 200:
                results.append(resp.content)
                print(f"  [image {idx + 1}] OK ({len(resp.content) // 1024} KB)")
                success = True
                break

            if resp.status_code == 503:
                try:
                    wait = float(resp.json().get("estimated_time", RETRY_SLEEP))
                except Exception:
                    wait = RETRY_SLEEP
                wait = min(wait, 90)
                print(f"  [image] model loading — waiting {wait:.0f}s …")
                time.sleep(wait)
                continue

            print(f"  [image] HTTP {resp.status_code} — skipping")
            break

        if not success:
            print(f"  [image {idx + 1}] using gradient fallback")
            results.append(_gradient_fallback(idx))

        time.sleep(2)   # polite rate-limiting

    return results


# ─────────────────────────────────────────────
# Fallback: generate a simple gradient in memory
# ─────────────────────────────────────────────

def _gradient_fallback(seed: int, w: int = 1280, h: int = 720) -> bytes:
    """Return JPEG bytes of a vertical gradient."""
    c1, c2 = FALLBACK_PALETTES[seed % len(FALLBACK_PALETTES)]
    img  = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    for y in range(h):
        t   = y / h
        rgb = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        draw.line([(0, y), (w, y)], fill=rgb)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()
