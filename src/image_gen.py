"""
image_gen.py
Primary  : Pollinations.ai — FREE, no API key, no rate limit, uses FLUX model
Fallback : Pillow gradient (always works)
"""
import io, time, random, urllib.parse
import requests
from PIL import Image, ImageDraw


STYLE_TAGS = [
    "cinematic lighting, 4k, atmospheric",
    "oil painting style, vibrant colors, detailed",
    "watercolor art, soft pastel tones, dreamy",
    "digital art, dramatic lighting, photorealistic",
    "golden hour photography, warm tones",
    "moody atmospheric, deep colors, mystical",
]

FALLBACK_PALETTES = [
    [(20, 0, 50),  (80, 0, 120)],
    [(0, 20, 60),  (0, 80, 160)],
    [(40, 10, 0),  (140, 60, 0)],
    [(5, 30, 10),  (20, 100, 40)],
    [(30, 0, 0),   (110, 20, 20)],
    [(10, 10, 40), (60, 60, 160)],
]


def _pollinations(prompt: str, seed: int) -> bytes | None:
    """
    Pollinations.ai — completely free, no API key needed.
    Uses FLUX model, returns 1280×720 JPEG.
    """
    encoded = urllib.parse.quote(prompt)
    url = (f"https://image.pollinations.ai/prompt/{encoded}"
           f"?width=1280&height=720&seed={seed}&nologo=true&model=flux")
    try:
        r = requests.get(url, timeout=90)
        if r.status_code == 200 and len(r.content) > 5000:
            # Convert to JPEG via Pillow to ensure correct format
            img = Image.open(io.BytesIO(r.content)).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            return buf.getvalue()
        print(f"    pollinations HTTP {r.status_code}")
    except Exception as e:
        print(f"    pollinations error: {str(e)[:80]}")
    return None


def generate_images(prompts: list, hf_token: str) -> list:
    """hf_token kept for API compatibility but not used — Pollinations needs no key."""
    results = []

    for idx, prompt in enumerate(prompts):
        style       = random.choice(STYLE_TAGS)
        full_prompt = f"{prompt}, {style}"
        seed        = random.randint(1, 99999)
        img_bytes   = None

        print(f"  [image {idx+1}/{len(prompts)}] generating via Pollinations.ai …")

        # Try Pollinations up to 3 times (different seeds)
        for attempt in range(3):
            img_bytes = _pollinations(full_prompt, seed + attempt * 1000)
            if img_bytes:
                print(f"  [image {idx+1}] OK ({len(img_bytes)//1024} KB) ✓")
                break
            time.sleep(5)

        if img_bytes is None:
            print(f"  [image {idx+1}] using gradient fallback")
            img_bytes = _gradient_fallback(idx)

        results.append(img_bytes)
        time.sleep(2)   # be polite

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
