"""
lyrics_overlay.py
Overlays song lyrics onto a romantic couple image.
Creates a beautiful lyric-video style frame with gradient overlay and text.
"""
import io, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

W, H = 1280, 720

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
]

# Colors per section type
SECTION_COLORS = {
    "chorus"   : (255, 220, 100),   # warm gold
    "bridge"   : (180, 220, 255),   # soft blue
    "outro"    : (200, 255, 200),   # soft green
    "prechorus": (255, 180, 200),   # soft pink
    "verse"    : (255, 255, 255),   # white
}


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for p in FONT_PATHS:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def add_lyrics(image_bytes: bytes, lines: list,
               section_type: str = "verse",
               song_title: str = "") -> bytes:
    """
    Overlay lyrics lines on a romantic image.

    Args:
        image_bytes  : Raw JPEG/PNG bytes of the background image.
        lines        : List of lyric strings to display.
        section_type : 'verse', 'chorus', 'bridge', etc.
        song_title   : Shown in small text at top.

    Returns:
        JPEG bytes of the finished lyric frame.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Resize to target
    img = _fill_crop(img, W, H)

    # Subtle blur for text readability
    blurred = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    img = Image.blend(img, blurred, alpha=0.25)

    # ── Bottom gradient overlay ───────────────────────────────────────────
    overlay    = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov    = ImageDraw.Draw(overlay)
    grad_start = int(H * 0.42)
    for y in range(grad_start, H):
        progress = (y - grad_start) / (H - grad_start)
        alpha    = int(210 * (progress ** 1.3))
        draw_ov.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    img  = img.convert("RGBA")
    img  = Image.alpha_composite(img, overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # ── Song title (small, top centre) ───────────────────────────────────
    if song_title:
        font_title = _load_font(22)
        clean_title = song_title[:60]
        bbox = draw.textbbox((0, 0), clean_title, font=font_title)
        tx = (W - (bbox[2] - bbox[0])) // 2
        draw.text((tx+1, 16), clean_title, font=font_title, fill=(0, 0, 0, 160))
        draw.text((tx, 15), clean_title, font=font_title, fill=(200, 200, 200))

    # ── Lyrics lines ─────────────────────────────────────────────────────
    text_color  = SECTION_COLORS.get(section_type, (255, 255, 255))
    n_lines     = len(lines)
    font_size   = 44 if n_lines <= 2 else (38 if n_lines == 3 else 32)
    font        = _load_font(font_size)
    line_height = font_size + 14

    total_text_h = n_lines * line_height
    y_start      = H - total_text_h - 55

    for line in lines:
        bbox  = draw.textbbox((0, 0), line, font=font)
        tw    = bbox[2] - bbox[0]
        x     = (W - tw) // 2

        # Drop shadow
        draw.text((x+2, y_start+2), line, font=font, fill=(0, 0, 0))
        # Main text
        draw.text((x, y_start), line, font=font, fill=text_color)
        y_start += line_height

    # ── Section badge (chorus/bridge only) ───────────────────────────────
    if section_type in ("chorus", "bridge"):
        badge_font = _load_font(18)
        badge_text = f"♪ {section_type.upper()} ♪"
        bbox       = draw.textbbox((0, 0), badge_text, font=badge_font)
        bw, bh     = bbox[2] - bbox[0], bbox[3] - bbox[1]
        bx, by     = 16, H - bh - 20
        draw.rounded_rectangle(
            [bx-6, by-4, bx+bw+6, by+bh+4],
            radius=6,
            fill=text_color + (180,) if len(text_color) == 3 else text_color,
        )
        draw.text((bx, by), badge_text, font=badge_font, fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def _fill_crop(img: Image.Image, w: int, h: int) -> Image.Image:
    ow, oh = img.size
    scale  = max(w / ow, h / oh)
    nw, nh = int(ow * scale), int(oh * scale)
    img    = img.resize((nw, nh), Image.LANCZOS)
    left   = (nw - w) // 2
    top    = (nh - h) // 2
    return img.crop((left, top, left + w, top + h))
