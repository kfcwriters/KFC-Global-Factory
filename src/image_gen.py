"""
image_gen.py
Generates images via direct requests to HuggingFace endpoints.
Falls back to Pillow gradient — always succeeds.
"""
import io
import time
import random
import requests
from PIL import Image, ImageDraw


HF_ENDPOINTS = [
    "https://router.huggingface.co/hf-inference/models/{model}",
    "https://api-inference.huggingface.co/models/{model}",
]

IMAGE_MODELS = [
    "stabilityai/stable-diffusion-xl-base-1.0",
    "stabilityai/stable-diffusion-2-1",
    "runwayml/stable-diffusion-v1-5",
]

STYLE_TAGS = [
    "cinematic lighting, 4k, atmospheric, ultra detailed",
    "oil painting style, vibrant colors, rich texture",
    "watercolor art, soft pastel tones, dreamy, ethereal",
    "digital art, dramatic shadows, photorealistic",
    "golden hour photography, warm tones, depth of field",
    "moody dark fantasy, deep shadows, mystical",
]

FALLBACK_PALETTES = [
    [(20, 0, 50),  (80, 0, 120)],
    [(0, 20, 60),  (0, 80, 160)],
    [(40, 10, 0),  (140, 60, 0)],
    [(5, 30, 10),  (20, 100, 40)],
    [(30, 0, 0),   (110, 20, 20)],
]


def generate_images(prompts: list, hf_token: str) -> list:
    headers = {"Authorization": f"Bearer {hf_token}"}
    results = []

    for idx, prompt in enumerate(prompts):
        style       = random.choice(STYLE_TAGS)
        full_prompt = f"{prompt}, {style}"
        img_bytes   = None

        # Try each endpoint × each model
        outer:
        for base_url in HF_ENDPOINTS:
            for model in IMAGE_MODELS:
                url     = base_url.format(model=model)
                payload = {
                    "inputs": full_prompt,
                    "parameters": {"width": 1280, "height": 720}
                }
                print(f"  [image {idx+1}/{len(prompts)}] {model.split('/')[-1]} …")
                try:
                    resp = requests.post(url, headers=headers, json=payload, timeout=90)
                    if resp.status_code == 200:
                        pil_img = Image.open(io.BytesIO(resp.content)).convert("RGB")
                        buf = io.BytesIO()
                        pil_img.save(buf, format="JPEG", quality=90)
                        img_bytes = buf.getvalue()
                        print(f"  [image {idx+1}] OK ({len(img_bytes)//1024} KB) ✓")
                        break
                    elif resp.status_code == 503:
                        time.sleep(35)
                    else:
                        print(f"  [image {idx+1}] HTTP {resp.status_code}")
                except Exception as exc:
                    print(f"  [image {idx+1}] {str(exc)[:80]}")
                    time.sleep(10)
            if img_bytes:
                break

        if img_bytes is None:
            print(f"  [image {idx+1}] all endpoints failed — gradient fallback")
            img_bytes = _gradient_fallback(idx)

        results.append(img_bytes)
        time.sleep(3)

    return results


def _gradient_fallback(seed: int, w: int = 1280, h: int = 720) -> bytes:
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
