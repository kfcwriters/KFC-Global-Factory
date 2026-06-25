"""
thumbnail_gen.py
Creates a YouTube-optimised 1280×720 thumbnail from the first AI image.
Uses Pillow only — no extra deps.
"""

import io
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


THUMB_W, THUMB_H = 1280, 720

# Font paths available on ubuntu-latest
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
]


def create_thumbnail(image_bytes: bytes, title: str, output_path: str) -> str:
    """
    Build a thumbnail and save it as JPEG.

    Args:
        image_bytes : Raw bytes of the base image.
        title       : Video title (used as overlay text).
        output_path : Destination file path (should end in .jpg).

    Returns:
        output_path on success.
    """
    # ── 1. Load & resize base image ──────────────────────────────────────────
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = _fill_crop(img, THUMB_W, THUMB_H)

    # ── 2. Slight blur + darken for text legibility ───────────────────────────
    blurred = img.filter(ImageFilter.GaussianBlur(radius=1))
    img     = Image.blend(img, blurred, alpha=0.3)

    # ── 3. Dark gradient overlay at bottom half ───────────────────────────────
    overlay = Image.new("RGBA", (THUMB_W, THUMB_H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    grad_start = int(THUMB_H * 0.45)
    for y in range(grad_start, THUMB_H):
        progress = (y - grad_start) / (THUMB_H - grad_start)
        alpha    = int(200 * progress ** 1.5)
        draw_ov.line([(0, y), (THUMB_W, y)], fill=(0, 0, 0, alpha))

    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay).convert("RGB")

    # ── 4. Prepare text ───────────────────────────────────────────────────────
    clean_title = _strip_emoji(title).strip()
    font_lg     = _load_font(60)
    font_sm     = _load_font(28)
    draw        = ImageDraw.Draw(img)

    # Wrap title to max 2 lines, ~30 chars each
    lines = textwrap.wrap(clean_title, width=32)[:2]

    # ── 5. Draw title text (shadow + white) ───────────────────────────────────
    line_h   = 70
    total_h  = len(lines) * line_h
    y_start  = THUMB_H - total_h - 55

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_lg)
        tw   = bbox[2] - bbox[0]
        x    = (THUMB_W - tw) // 2
        # Shadow
        draw.text((x + 3, y_start + 3), line, font=font_lg, fill=(0, 0, 0, 180))
        # Text
        draw.text((x, y_start), line, font=font_lg, fill=(255, 255, 255))
        y_start += line_h

    # ── 6. "AI GENERATED" badge top-left ─────────────────────────────────────
    badge_text = "AI GENERATED"
    bx, by     = 18, 18
    bbox       = draw.textbbox((bx, by), badge_text, font=font_sm)
    padding    = 8
    draw.rounded_rectangle(
        [bbox[0] - padding, bbox[1] - padding,
         bbox[2] + padding, bbox[3] + padding],
        radius=6,
        fill=(255, 180, 0)
    )
    draw.text((bx, by), badge_text, font=font_sm, fill=(0, 0, 0))

    # ── 7. Save ───────────────────────────────────────────────────────────────
    img.save(output_path, "JPEG", quality=95, optimize=True)
    print(f"  [thumb] saved {output_path}")
    return output_path


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────

def _fill_crop(img: Image.Image, w: int, h: int) -> Image.Image:
    """Scale image to fill w×h then center-crop."""
    orig_w, orig_h = img.size
    scale = max(w / orig_w, h / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    img   = img.resize((new_w, new_h), Image.LANCZOS)
    left  = (new_w - w) // 2
    top   = (new_h - h) // 2
    return img.crop((left, top, left + w, top + h))


def _strip_emoji(text: str) -> str:
    """Remove emoji / non-latin characters for font compatibility."""
    return re.sub(r"[^\x00-\x7F]+", "", text)


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()
