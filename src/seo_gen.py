"""
seo_gen.py
Generates SEO-optimized YouTube titles, descriptions and tags.

Uses proven YouTube title formulas that actually rank and get clicks.
Research shows these patterns consistently outperform generic titles.
"""
import random
from datetime import datetime

YEAR = datetime.utcnow().year

# ── Proven English romantic song title formulas ────────────────────────────────
ENGLISH_TITLE_FORMULAS = [
    "{title} 💔 Sad Romantic Song That Will Make You Cry {year}",
    "{title} ❤️ Best Romantic Love Song {year} | Heart Touching",
    "{title} 😢 Most Emotional Love Song {year} | Miss You Song",
    "{title} 🌹 Beautiful Romantic Song {year} | True Love",
    "{title} 💕 Soft Romantic Song {year} | Love Song for Her",
    "Heart Touching Love Song 💔 {title} | Sad Song {year}",
    "{title} | Romantic Ballad {year} 🎵 Emotional Love Song",
    "Miss You Song 😢 {title} | Heart Broken Song {year}",
    "{title} 💖 Sweet Romantic Song | Best Love Song {year}",
    "Emotional Love Song 🥺 {title} | Romantic Song {year}",
]

# ── Proven Hindi song title formulas ──────────────────────────────────────────
HINDI_TITLE_FORMULAS = [
    "{title} 💔 Dard Bhara Song {year} | Hindi Sad Song",
    "{title} ❤️ Best Hindi Romantic Song {year} | Dil Se",
    "{title} 😢 Emotional Hindi Song {year} | Miss You",
    "{title} 🌹 Pyaar Ka Song {year} | Hindi Love Song",
    "Dil Tuta Song 💔 {title} | Hindi Sad Song {year}",
    "{title} | Hindi Romantic Song {year} 🎵 Feeling",
    "{title} 💕 Mohabbat Song {year} | Dil Ki Baat",
    "Hindi Sad Song 😢 {title} | Judai Song {year}",
    "{title} 💖 Pyar Wala Song | Best Hindi Song {year}",
    "Emotional Hindi Song 🥺 {title} | Romantic {year}",
]

# ── Tag sets ──────────────────────────────────────────────────────────────────
ENGLISH_TAGS = [
    "romantic love song", "sad love song", "emotional song",
    "heart touching song", "best love song 2026", "miss you song",
    "romantic music", "love song 2026", "beautiful love song",
    "soft romantic song", "true love song", "english love song",
    "new romantic song", "romantic ballad", "heart broken song",
]

HINDI_TAGS = [
    "hindi sad song", "hindi romantic song", "dard bhara song",
    "hindi love song 2026", "pyar ka song", "emotional hindi song",
    "dil tuta song", "hindi new song", "mohabbat song",
    "best hindi song 2026", "judai song", "hindi feeling song",
    "new hindi song", "romantic hindi song", "dil se song",
]

# ── Description templates ─────────────────────────────────────────────────────
ENGLISH_DESC = """🎵 {title} — A beautiful romantic love song that touches your heart.

❤️ If you love romantic songs, this one is for you. Share this song with someone special.

🔔 Subscribe for new romantic songs every week!
👍 Like if this song touched your heart
💬 Comment the name of your special someone below

━━━━━━━━━━━━━━━━━━━━━━━
🎵 More Romantic Songs → @HeartfullSongsOfficial
━━━━━━━━━━━━━━━━━━━━━━━

#RomanticSong #LoveSong #HeartTouchingSong #SadSong #EmotionalSong
#RomanticMusic #LoveSongs2026 #BestLoveSong #MissYouSong #NewSong2026
"""

HINDI_DESC = """🎵 {title} — Ek dil ko chhu lene wala romantic Hindi song.

❤️ Agar aapko Hindi romantic songs pasand hain, toh ye song zaroor sunein.
Apne kisi khas insaan ke saath share karein! 💕

🔔 Subscribe karein nayi romantic songs ke liye!
👍 Like karein agar ye song aapke dil ko chhu gaya
💬 Comment mein apne special someone ka naam likhein

━━━━━━━━━━━━━━━━━━━━━━━
🎵 Aur Hindi Songs → @Bestmixsoulfullmusic
━━━━━━━━━━━━━━━━━━━━━━━

#HindiSong #HindiRomanticSong #SadHindiSong #DilKaSong #LoveSongHindi
#HindiNewSong2026 #PyarKaSong #EmotionalHindiSong #BestHindiSong #DardBharaSong
"""


def generate_seo(title: str, content_type: str = "romantic songs",
                 style: str = "") -> dict:
    """
    Generate SEO-optimized metadata for YouTube.

    Args:
        title        : Song title
        content_type : "romantic songs" or "hindi songs"
        style        : Music style string

    Returns:
        dict with title, description, tags
    """
    is_hindi = "hindi" in content_type.lower() or "hindi" in style.lower()

    # Clean title — remove generic suffixes our pipeline adds
    clean = title
    for remove in ["Beautiful Love Song", "Best Romantic Song 2026 -",
                   "| AI Music Cover | Emotional Ballad",
                   "🌹 Hindi Romantic Song 🌹", "🎵 Beautiful Romantic Love Song 2026"]:
        clean = clean.replace(remove, "").strip(" -|")
    clean = clean.strip()
    if not clean or len(clean) < 3:
        clean = title

    # Pick title formula
    if is_hindi:
        formula = random.choice(HINDI_TITLE_FORMULAS)
        tags = HINDI_TAGS[:13]
        description = HINDI_DESC.format(title=clean)
    else:
        formula = random.choice(ENGLISH_TITLE_FORMULAS)
        tags = ENGLISH_TAGS[:13]
        description = ENGLISH_DESC.format(title=clean)

    yt_title = formula.format(title=clean, year=YEAR)[:100]

    print(f"  [seo] Title: {yt_title}")

    return {
        "title"      : yt_title,
        "description": description,
        "tags"       : tags,
    }


def make_shorts_seo(title: str, is_hindi: bool = False) -> dict:
    """Generate SEO for YouTube Shorts."""
    clean = title.strip()

    if is_hindi:
        shorts_title = f"#Shorts 😢 {clean} | Hindi Sad Song | #HindiSong #Romantic"[:100]
        tags = ["shorts", "hindi shorts", "hindi sad song shorts",
                "romantic hindi shorts", "love song shorts",
                "hindi song shorts", "emotional shorts"]
        desc = f"#Shorts #HindiSong #RomanticSong\n{clean} 💔\n\n🔔 Subscribe for more!"
    else:
        shorts_title = f"#Shorts 💔 {clean} | Sad Romantic Song | #LoveSong #Romantic"[:100]
        tags = ["shorts", "romantic shorts", "sad song shorts",
                "love song shorts", "emotional shorts",
                "romantic song shorts", "heart touching shorts"]
        desc = f"#Shorts #LoveSong #RomanticSong\n{clean} 💔\n\n🔔 Subscribe for more!"

    return {"title": shorts_title, "description": desc, "tags": tags}
