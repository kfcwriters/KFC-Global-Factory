"""
lyrics_writer_hindi.py
Generates 100% unique Hindi (Romanized) romantic song lyrics every week.
Pure Python — no API needed, completely free, works forever.
Same technique as lyrics_writer.py (English) — different word banks.

Uses Romanized Hindi (Hindi words in English script) since ACE-Step's
text encoder handles Latin script much better than Devanagari for singing.
"""
import random
from datetime import datetime


# ── Hindi word banks (Romanized) ──────────────────────────────────────────────
NAMES_OF_LOVE = [
    "meri jaan", "mera dil", "meri zindagi", "mera pyaar", "meri dhadkan",
    "mera chand", "mera sitara", "meri khushi", "mera sukoon", "meri duniya",
    "meri saans", "mera nasha", "meri mohabbat", "mera armaan",
]

FEELINGS = [
    "tujhse pyaar ho gaya", "tere bina adhoora hoon",
    "tujhe dekh ke sukoon milta hai", "zindagi khoobsurat lagti hai",
    "dil ki dhadkan badh jaati hai", "har gham bhool jaata hoon",
    "naya jahan mil gaya", "khushiyon ka ehsaas hota hai",
    "tere ishq mein doob gaya", "har pal tera intezaar karta hoon",
]

NATURE_IMAGES = [
    "chaand roshni bikhrata hai", "sitare aasman mein chamakte hain",
    "phool khilte hain baagon mein", "baarish barasti hai dheere dheere",
    "hawa tera naam leti hai", "samandar ki lehrein gaati hain",
    "suraj dhalta hai shaam mein", "titliyan udti hain baagon mein",
    "kohra chaaya hai pahaadon par", "patte girte hain khamoshi se",
]

PROMISES = [
    "main tujhe kabhi nahi chhodunga",
    "hamesha tera saath dunga",
    "main tere saath hoon har pal",
    "tujhe kabhi akela nahi chhodunga",
    "har janam mein tujhe chahunga",
    "tera haath kabhi nahi chhodunga",
    "zindagi bhar tera intezaar karunga",
    "tujhse pyaar karta rahunga hamesha",
]

ENGLISH_MIX_LINES = [
    ("You are my everything", "Tu hi meri sab kuch hai"),
    ("I will always love you", "Main hamesha tujhe pyaar karunga"),
    ("Forever and always", "Hamesha aur hamesha"),
    ("You complete my heart", "Tu mera dil poora karta hai"),
    ("My heart beats for you", "Mera dil tere liye dhadakta hai"),
    ("You are my dream come true", "Tu meri poori hui khwaish hai"),
    ("Stay with me forever", "Mere saath hamesha reh"),
    ("I found my home in you", "Tujhme mera ghar mil gaya"),
]

MOODS = [
    "sacha pyaar", "judaai ka dard", "pehla pyaar", "hamesha ka saath",
    "rooh se rooh ka milan", "baarish mein pyaar", "shaadi ka vaada",
    "doori aur intezaar", "milan ki khushi", "khamosh mohabbat",
    "jazbaati pyaar", "himmat wala pyaar", "shukrguzaar pyaar",
    "dil se dil ki baat", "pehla ishq",
]

MUSIC_STYLES = [
    "bollywood romantic ballad, soft piano, emotional female vocals, slow tempo",
    "sad hindi ballad, piano and violin, melancholic female vocals",
    "upbeat hindi pop, dhol and guitar, happy female vocals",
    "bollywood fusion, sitar and tabla, Hindi female vocals, soulful",
    "orchestral hindi romantic, strings and piano, powerful female vocals",
    "soft intimate hindi ballad, acoustic guitar, whispery female vocals",
    "monsoon hindi romantic, piano and rain sounds, dreamy female vocals",
    "hindi wedding song, dhol and shehnai, uplifting female vocals",
    "hindi qawwali inspired, harmonium and tabla, soulful female vocals",
    "bollywood RnB, piano and beats, deep emotional female vocals",
]

SONG_TITLES = [
    "Tere Bina", "Mera Ishq", "Dil Ki Baat", "Pyaar Ka Rang",
    "Tu Hi Meri Duniya", "Judaai", "Milan", "Zindagi Tere Naam",
    "Chaand Sitare", "Baarish Aur Tu", "Dil Se Dil Tak",
    "Mohabbat Ki Kahani", "Tere Ishq Mein", "Saath Hai Tu",
    "Dooriyan",
]


def _title(week: int) -> str:
    return SONG_TITLES[week % len(SONG_TITLES)]


def _verse(week: int, verse_num: int) -> list:
    seed = week * 10 + verse_num
    r    = random.Random(seed)

    lines = [
        f"{r.choice(NATURE_IMAGES).capitalize()}",
        f"Aur {r.choice(FEELINGS)}",
        f"Tu hai {r.choice(NAMES_OF_LOVE)}",
        f"{r.choice(PROMISES)}",
    ]
    return lines


def _chorus(week: int) -> list:
    r = random.Random(week * 100)
    eng, hin = r.choice(ENGLISH_MIX_LINES)

    lines = [
        f"Tu hai {r.choice(NAMES_OF_LOVE)}, tu hi sab kuch hai",
        f"{hin}",
        f"{r.choice(PROMISES)}",
        f"Tu hai {r.choice(NAMES_OF_LOVE)}, mera pyaar hamesha",
    ]
    return lines


def _bridge(week: int) -> list:
    r = random.Random(week * 200)
    eng, hin = r.choice(ENGLISH_MIX_LINES)

    lines = [
        f"{hin}",
        f"{eng}",
        f"{r.choice(PROMISES)}",
        f"Tu hai {r.choice(NAMES_OF_LOVE)} hamesha ke liye",
    ]
    return lines


def generate_weekly_lyrics_hindi() -> dict:
    """
    Generate completely unique Hindi lyrics every week.
    Same seeding technique as English version — reproducible per week,
    different across weeks.
    """
    week  = datetime.utcnow().isocalendar()[1]
    year  = datetime.utcnow().year
    seed  = week + year * 100 + 500   # offset so it differs from English seed

    random.seed(seed)

    title  = _title(week)
    style  = MUSIC_STYLES[week % len(MUSIC_STYLES)]
    mood   = MOODS[week % len(MOODS)]

    verse1 = _verse(week, 1)
    verse2 = _verse(week, 2)
    chorus = _chorus(week)
    bridge = _bridge(week)

    sections = [
        {"type": "verse",  "lines": verse1},
        {"type": "chorus", "lines": chorus},
        {"type": "verse",  "lines": verse2},
        {"type": "chorus", "lines": chorus},
        {"type": "bridge", "lines": bridge},
        {"type": "chorus", "lines": chorus},
    ]

    prompt = "\n\n".join(
        f"[{s['type']}]\n" + "\n".join(s["lines"]) for s in sections
    )

    print(f"  [lyrics-hindi] Week {week}/{year}: '{title}' ({mood})")
    print(f"  [lyrics-hindi] Style: {style[:50]}...")

    return {
        "title"    : title,
        "prompt"   : prompt,
        "style"    : style,
        "mood"     : mood,
        "sections" : sections,
    }
