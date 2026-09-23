"""
thumbnail_gen.py
Generates eye-catching YouTube thumbnails that actually get clicks.

Proven thumbnail formula for music channels:
- Bold emotional text (60% of thumbnail)
- High contrast colors (red/yellow/white on dark)
- Large readable font even on mobile
- Emotional trigger words that make people click
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import io, os, random


# Emotional trigger words that drive clicks on music channels
EMOTION_TAGS = [
    "💔 SAD", "❤️ LOVE", "😢 MISS YOU", "🥺 EMOTIONAL",
    "💕 ROMANTIC", "😍 BEAUTIFUL", "🌹 HEART", "✨ FEELING",
]

# High-contrast color schemes proven to get clicks
COLOR_SCHEMES = [
    {"bg": (20, 20, 40),    "accent": (255, 50, 50),   "text": (255, 255, 255)},   # Dark blue + Red
    {"bg": (30, 10, 10),    "accent": (255, 180, 0),   "text": (255, 255, 255)},   # Dark + Gold
    {"bg": (10, 30, 10),    "accent": (255, 80, 80),   "text": (255, 255, 255)},   # Dark green + Red
    {"bg": (20, 10, 40),    "accent": (255, 100, 200), "text": (255, 255, 255)},   # Purple + Pink
    {"bg": (40, 10, 10),    "accent": (255, 200, 50),  "text": (255, 255, 255)},   # Dark red + Yellow
]


def _get_font(size: int):
    """Get the best available bold font."""
    font_paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(text: str, max_chars: int = 18) -> list:
    """Wrap text to fit on thumbnail."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = (current + " " + word).strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:3]  # Max 3 lines


def create_thumbnail(
    image_bytes: bytes,
    title: str,
    output_path: str,
    is_hindi: bool = False,
) -> str:
    """
    Generate a high-CTR YouTube thumbnail.

    Layout:
    - Background: source image (darkened + blurred slightly)
    - Bottom gradient: dark overlay for text readability
    - Large bold title text
    - Colored accent bar
    - Emotion tag (top left)
    """
    # ── Base image ────────────────────────────────────────────────────────────
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        img = Image.new("RGB", (1280, 720), (20, 20, 40))

    img = img.resize((1280, 720), Image.LANCZOS)

    # Darken and slightly blur for text readability
    img = ImageEnhance.Brightness(img).enhance(0.55)
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))

    draw = ImageDraw.Draw(img)

    # ── Pick color scheme ─────────────────────────────────────────────────────
    scheme = random.choice(COLOR_SCHEMES)
    accent = scheme["accent"]
    text_color = scheme["text"]

    # ── Bottom gradient overlay ────────────────────────────────────────────────
    for y in range(300, 720):
        alpha = int(200 * (y - 300) / 420)
        for x in range(1280):
            r, g, b = img.getpixel((x, y))
            nr = int(r * (1 - alpha/255) + scheme["bg"][0] * (alpha/255))
            ng = int(g * (1 - alpha/255) + scheme["bg"][1] * (alpha/255))
            nb = int(b * (1 - alpha/255) + scheme["bg"][2] * (alpha/255))
            draw.point((x, y), (nr, ng, nb))

    # ── Accent bar (left side) ────────────────────────────────────────────────
    draw.rectangle([0, 0, 12, 720], fill=accent)

    # ── Emotion tag (top left) ────────────────────────────────────────────────
    emotion = random.choice(EMOTION_TAGS)
    tag_font = _get_font(36)
    draw.rectangle([20, 20, 280, 72], fill=accent)
    draw.text((30, 26), emotion, font=tag_font, fill=(255, 255, 255))

    # ── Main title text ───────────────────────────────────────────────────────
    # Clean title for display
    clean_title = title
    for emoji in ["🌹","💖","💕","❤️","🎵","✨","💔","😍","🥺","😢","🎶","🎤"]:
        clean_title = clean_title.replace(emoji, "")
    clean_title = clean_title.strip()

    # Remove SEO suffixes for cleaner thumbnail
    for suffix in [" | Romantic Ballad", " | Love Song", "Best Romantic Song 2026 -",
                   "- Romantic Ballad For Someone Special", "Beautiful Romantic Love Song 2026"]:
        clean_title = clean_title.replace(suffix, "").strip()

    lines = _wrap_text(clean_title.upper(), max_chars=16)

    # Large font for title
    title_font = _get_font(110)
    small_font = _get_font(80)

    y_start = 720 - (len(lines) * 120) - 60

    for i, line in enumerate(lines):
        font = title_font if i == 0 else small_font
        # Shadow for readability
        draw.text((32, y_start + i*115 + 2), line, font=font, fill=(0,0,0))
        draw.text((30, y_start + i*115), line, font=font, fill=text_color)

    # ── Accent underline ──────────────────────────────────────────────────────
    draw.rectangle([30, y_start - 8, 300, y_start - 2], fill=accent)

    # ── "New Song" badge (top right) ─────────────────────────────────────────
    badge_font = _get_font(32)
    draw.rectangle([1100, 20, 1270, 70], fill=accent)
    draw.text((1112, 28), "NEW SONG", font=badge_font, fill=(255,255,255))

    img.save(output_path, "JPEG", quality=95)
    print(f"  [thumb] saved {output_path}")
    return output_path
