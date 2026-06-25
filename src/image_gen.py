"""
image_gen.py
Generates images using the official huggingface_hub InferenceClient.
Falls back to a Pillow-drawn gradient if generation fails.
"""

import io
import time
import random
from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw


# Models to try in order (first one that works is used)
IMAGE_MODELS = [
    "stabilityai/stable-diffusion-xl-base-1.0",
    "stabilityai/stable-diffusion-2-1",
    "runwayml/stable-diffusion-v1-5",
]

STYLE_TAGS = [
    "cinematic lighting, 4k, atmospheric, ultra detailed",
    "oil painting style, vibrant colors, rich texture, artstation",
    "watercolor art, soft pastel tones, dreamy, ethereal",
    "digital art, dramatic shadows, photorealistic",
    "golden hour photography, warm tones, shallow depth of field",
    "moody dark fantasy, deep shadows, mystical atmosphere",
]

FALLBACK_PALETTES = [
    [(20, 0, 50),  (80, 0, 120)],
    [(0, 20, 60),  (0, 80, 160)],
    [(40, 10, 0),  (140, 60, 0)],
    [(5, 30, 10),  (20, 100, 40)],
    [(30, 0, 0),   (110, 20, 20)],
]


def generate_images(prompts: list[str], hf_token: str) -> list[bytes]:
    """
    Generate one image per prompt using HuggingFace InferenceClient.

    Args:
        prompts  : List of image description strings.
        hf_token : HuggingFace API token.

    Returns:
        List of JPEG bytes. Failed slots become gradient fallbacks.
    """
    client  = InferenceClient(token=hf_token)
    results = []

    for idx, prompt in enumerate(prompts):
        style      = random.choice(STYLE_TAGS)
        full_prompt = f"{prompt}, {style}"
        img_bytes  = None

        for model in IMAGE_MODELS:
            print(f"  [image {idx+1}/{len(prompts)}] trying {model.split('/')[-1]} …")
            try:
                pil_img = client.text_to_image(
                    full_prompt,
                    model=model,
                    width=1280,
                    height=720,
                )
                # text_to_image returns a PIL Image object
                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG", quality=90)
                img_bytes = buf.getvalue()
                print(f"  [image {idx+1}] OK ({len(img_bytes)//1024} KB)")
                break

            except Exception as exc:
                print(f"  [image {idx+1}] {model.split('/')[-1]} failed: {str(exc)[:120]}")
                time.sleep(10)

        if img_bytes is None:
            print(f"  [image {idx+1}] all models failed — using gradient fallback")
            img_bytes = _gradient_fallback(idx)

        results.append(img_bytes)
        time.sleep(3)   # polite rate-limiting between images

    return results


def _gradient_fallback(seed: int, w: int = 1280, h: int = 720) -> bytes:
    """Return JPEG bytes of a simple vertical gradient."""
    c1, c2 = FALLBACK_PALETTES[seed % len(FALLBACK_PALETTES)]
    img    = Image.new("RGB", (w, h))
    draw   = ImageDraw.Draw(img)
    for y in range(h):
        t   = y / h
        rgb = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        draw.line([(0, y), (w, y)], fill=rgb)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()
