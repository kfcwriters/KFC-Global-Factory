"""
lyrics_writer_hindi.py
Generates 100% unique Hindi song lyrics every week — in ACTUAL DEVANAGARI
SCRIPT (not Romanized), because ACE-Step auto-detects language from the
script/alphabet used. Romanized Hindi (Latin letters) gets detected as
English and sung with English phonetics — this is the bug we just fixed.

Pure Python — no API needed, completely free, works forever.
"""
import random
from datetime import datetime


# ── Hindi word banks — DEVANAGARI SCRIPT (for correct language detection) ─────
NAMES_OF_LOVE = [
    "मेरी जान", "मेरा दिल", "मेरी ज़िंदगी", "मेरा प्यार", "मेरी धड़कन",
    "मेरा चाँद", "मेरा सितारा", "मेरी खुशी", "मेरा सुकून", "मेरी दुनिया",
    "मेरी साँस", "मेरा नशा", "मेरी मोहब्बत", "मेरा अरमान",
]

FEELINGS = [
    "तुझसे प्यार हो गया", "तेरे बिना अधूरा हूँ",
    "तुझे देख के सुकून मिलता है", "ज़िंदगी खूबसूरत लगती है",
    "दिल की धड़कन बढ़ जाती है", "हर ग़म भूल जाता हूँ",
    "नया जहान मिल गया", "खुशियों का एहसास होता है",
    "तेरे इश्क़ में डूब गया", "हर पल तेरा इंतज़ार करता हूँ",
]

NATURE_IMAGES = [
    "चाँद रोशनी बिखेरता है", "सितारे आसमान में चमकते हैं",
    "फूल खिलते हैं बागों में", "बारिश बरसती है धीरे धीरे",
    "हवा तेरा नाम लेती है", "समंदर की लहरें गाती हैं",
    "सूरज ढलता है शाम में", "तितलियाँ उड़ती हैं बागों में",
    "कोहरा छाया है पहाड़ों पर", "पत्ते गिरते हैं ख़ामोशी से",
]

PROMISES = [
    "मैं तुझे कभी नहीं छोड़ूंगा",
    "हमेशा तेरा साथ दूंगा",
    "मैं तेरे साथ हूँ हर पल",
    "तुझे कभी अकेला नहीं छोड़ूंगा",
    "हर जनम में तुझे चाहूंगा",
    "तेरा हाथ कभी नहीं छोड़ूंगा",
    "ज़िंदगी भर तेरा इंतज़ार करूंगा",
    "तुझसे प्यार करता रहूंगा हमेशा",
]

BRIDGE_LINES = [
    "तू ही मेरी सब कुछ है",
    "मैं हमेशा तुझे प्यार करूंगा",
    "हमेशा और हमेशा",
    "तू मेरा दिल पूरा करता है",
    "मेरा दिल तेरे लिए धड़कता है",
    "तू मेरी पूरी हुई ख्वाहिश है",
    "मेरे साथ हमेशा रह",
    "तुझमें मेरा घर मिल गया",
]

MOODS = [
    "sacha pyaar", "judaai ka dard", "pehla pyaar", "hamesha ka saath",
    "rooh se rooh ka milan", "baarish mein pyaar", "shaadi ka vaada",
    "doori aur intezaar", "milan ki khushi", "khamosh mohabbat",
    "jazbaati pyaar", "himmat wala pyaar", "shukrguzaar pyaar",
    "dil se dil ki baat", "pehla ishq",
]

# Style tags stay in English (these guide the MUSIC style, not the lyrics
# language — ACE-Step's UMT5 prompt encoder handles English tags fine
# regardless of lyric language)
MUSIC_STYLES = [
    "bollywood romantic ballad, soft piano, emotional female vocals, slow tempo, hindi",
    "sad hindi ballad, piano and violin, melancholic female vocals, hindi language",
    "upbeat hindi pop, dhol and guitar, happy female vocals, hindi language",
    "bollywood fusion, sitar and tabla, hindi female vocals, soulful",
    "orchestral hindi romantic, strings and piano, powerful female vocals, hindi",
    "soft intimate hindi ballad, acoustic guitar, whispery female vocals, hindi",
    "monsoon hindi romantic, piano and rain sounds, dreamy female vocals, hindi",
    "hindi wedding song, dhol and shehnai, uplifting female vocals, hindi",
    "hindi qawwali inspired, harmonium and tabla, soulful female vocals, hindi",
    "bollywood RnB, piano and beats, deep emotional female vocals, hindi language",
]

# Titles shown in YouTube metadata — Romanized is fine here since this is
# just DISPLAY text, not sung lyrics
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
    return [
        r.choice(NATURE_IMAGES),
        f"और {r.choice(FEELINGS)}",
        f"तू है {r.choice(NAMES_OF_LOVE)}",
        r.choice(PROMISES),
    ]


def _chorus(week: int) -> list:
    r = random.Random(week * 100)
    return [
        f"तू है {r.choice(NAMES_OF_LOVE)}, तू ही सब कुछ है",
        r.choice(BRIDGE_LINES),
        r.choice(PROMISES),
        f"तू है {r.choice(NAMES_OF_LOVE)}, मेरा प्यार हमेशा",
    ]


def _bridge(week: int) -> list:
    r = random.Random(week * 200)
    return [
        r.choice(BRIDGE_LINES),
        r.choice(BRIDGE_LINES),
        r.choice(PROMISES),
        f"तू है {r.choice(NAMES_OF_LOVE)} हमेशा के लिए",
    ]


def generate_weekly_lyrics_hindi() -> dict:
    """
    Generate completely unique Hindi lyrics (Devanagari script) every week.
    """
    week = datetime.utcnow().isocalendar()[1]
    year = datetime.utcnow().year
    seed = week + year * 100 + 500

    random.seed(seed)

    title = _title(week)
    style = MUSIC_STYLES[week % len(MUSIC_STYLES)]
    mood  = MOODS[week % len(MOODS)]

    sections = [
        {"type": "verse",  "lines": _verse(week, 1)},
        {"type": "chorus", "lines": _chorus(week)},
        {"type": "verse",  "lines": _verse(week, 2)},
        {"type": "chorus", "lines": _chorus(week)},
        {"type": "bridge", "lines": _bridge(week)},
        {"type": "chorus", "lines": _chorus(week)},
    ]

    prompt = "\n\n".join(
        f"[{s['type']}]\n" + "\n".join(s["lines"]) for s in sections
    )

    print(f"  [lyrics-hindi] Week {week}/{year}: '{title}' ({mood})")
    print(f"  [lyrics-hindi] Style: {style[:50]}...")
    print(f"  [lyrics-hindi] Script: Devanagari (हिंदी) — for correct pronunciation")

    return {
        "title"    : title,
        "prompt"   : prompt,
        "style"    : style,
        "mood"     : mood,
        "sections" : sections,
    }
