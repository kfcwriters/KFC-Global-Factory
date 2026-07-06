"""
Creates a simple YouTube thumbnail: the background image + a title
overlay, using Pillow (free, no API).
"""
import os
from PIL import Image, ImageDraw, ImageFont


def _get_font(size: int):
    # Try a few common system fonts; fall back to Pillow's default bitmap font.
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def generate_thumbnail(background_path: str, title_text: str, out_path: str,
                        width: int = 1280, height: int = 720):
    img = Image.open(background_path).convert("RGB").resize((width, height))

    # Darken the lower third so text is readable.
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([0, height - 260, width, height], fill=(0, 0, 0, 140))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)
    font = _get_font(64)

    # Simple word-wrap so long titles don't run off the thumbnail.
    words = title_text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > width - 80:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    lines = lines[:2]  # cap at 2 lines so it stays readable

    y = height - 230
    for line in lines:
        draw.text((40, y), line, font=font, fill=(255, 255, 255))
        y += 75

    img.save(out_path, quality=90)


if __name__ == "__main__":
    generate_thumbnail("test_image.png", "Thyroid Health Music", "test_thumb.jpg")
