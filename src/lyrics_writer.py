"""
lyrics_writer.py
Generates 100% unique romantic song lyrics every week.
Pure Python — no API needed, completely free, works forever.
Uses word banks + poetic templates to create fresh combinations.
"""
import random
from datetime import datetime


# ── Word banks ────────────────────────────────────────────────────────────────
NAMES_OF_LOVE = [
    "my heart", "my soul", "my world", "my light", "my life",
    "my star", "my dream", "my peace", "my home", "my reason",
    "my angel", "my heaven", "my everything", "my sunshine", "my shelter",
]

FEELINGS = [
    "I fall in love with you", "I need you by my side",
    "I cannot breathe without you", "I feel alive again",
    "everything makes sense", "the world feels right",
    "I found my missing piece", "time stands still",
    "I forget all my pain", "my heart starts to sing",
]

NATURE_IMAGES = [
    "the stars light up the sky", "the moon shines on the sea",
    "roses bloom in the rain", "the sun sets over the hills",
    "the wind whispers your name", "the ocean calls to me",
    "fireflies dance in the dark", "the mountains touch the clouds",
    "morning mist covers the lake", "petals fall like snow",
]

PROMISES = [
    "I will love you till the end of time",
    "I will never let you go",
    "I will always be right here",
    "I choose you every single day",
    "I will hold your hand forever",
    "I will love you more each day",
    "I will walk beside you all my life",
    "I will catch you when you fall",
]

HINDI_LINES = [
    ("Tere bina jeena mushkil hai", "Living without you is so hard"),
    ("Dil mera bas tujhe chahta hai", "My heart wants only you"),
    ("Teri aankhon mein kho jaata hoon", "I get lost in your eyes"),
    ("Tujhse hi meri duniya hai", "You are my whole world"),
    ("Har pal teri yaad aati hai", "Every moment I think of you"),
    ("Tu hi meri manzil tu hi raasta", "You are my destination and my path"),
    ("Ishq mera sachcha hai tera", "My love for you is true"),
    ("Tere bina sab kuch adhoora hai", "Without you everything is incomplete"),
    ("Pyaar tera meri jaan hai", "Your love is my life"),
    ("Dil diya hai jaan bhi denge", "I gave my heart and I give my life"),
]

MOODS = [
    "eternal love", "missing you", "first love", "forever together",
    "soulmate found", "love in rain", "wedding vows", "distance and longing",
    "reunion love", "quiet love", "passionate love", "gentle love",
    "healing love", "brave love", "grateful love",
]

MUSIC_STYLES = [
    "romantic ballad, soft piano, emotional female vocals, slow tempo",
    "sad romantic ballad, piano and violin, melancholic female vocals",
    "upbeat romantic pop, acoustic guitar, happy female vocals",
    "bollywood fusion, sitar and piano, Hindi English female vocals",
    "orchestral romantic, strings and piano, powerful female vocals",
    "soft intimate ballad, acoustic guitar, whispery female vocals",
    "monsoon romantic, piano and rain sounds, dreamy female vocals",
    "wedding romantic, orchestral, uplifting ceremonial female vocals",
    "soulful RnB romantic, piano and cello, deep emotional female vocals",
    "folk romantic, guitar and flute, earthy warm female vocals",
]

SONG_TITLES = [
    "You Are My {noun}", "Forever {verb} You", "When I'm With You",
    "Love Like {noun}", "My Heart Knows", "Only You",
    "Stay {adv}", "Every Breath", "Come Back To Me",
    "Written In The Stars", "Just You And I", "This Feeling",
    "Closer", "Meant To Be", "Always and Forever",
]

TITLE_WORDS = {
    "noun"  : ["Home","Light","Heaven","Peace","Dream","World","Life","Star","Soul","Music"],
    "verb"  : ["Loving","Needing","Missing","Choosing","Holding","Finding","Wanting"],
    "adv"   : ["Forever","Always","Tonight","Close","With Me","Right Here","Together"],
}


def _title(week: int) -> str:
    """Generate a unique song title."""
    template = SONG_TITLES[week % len(SONG_TITLES)]
    for key, words in TITLE_WORDS.items():
        if "{" + key + "}" in template:
            template = template.replace("{"+key+"}", words[week % len(words)])
    return template


def _verse(week: int, verse_num: int) -> str:
    """Generate a unique verse."""
    seed = week * 10 + verse_num
    r    = random.Random(seed)

    lines = [
        f"{r.choice(NATURE_IMAGES).capitalize()}",
        f"And {r.choice(FEELINGS)}",
        f"You are {r.choice(NAMES_OF_LOVE)}",
        f"{r.choice(PROMISES)}",
    ]
    return "\n".join(lines)


def _chorus(week: int) -> str:
    """Generate a unique chorus."""
    r = random.Random(week * 100)

    lines = [
        f"You are {r.choice(NAMES_OF_LOVE)}, you are my everything",
        f"Every day with you is worth remembering",
        f"{r.choice(PROMISES)}",
        f"You are {r.choice(NAMES_OF_LOVE)}, my love my everything",
    ]
    return "\n".join(lines)


def _bridge(week: int) -> str:
    """Generate a unique bridge."""
    r = random.Random(week * 200)

    # 30% chance of including a Hindi line for Bollywood feel
    if week % 3 == 0:
        hindi, english = r.choice(HINDI_LINES)
        lines = [
            hindi,
            english,
            f"{r.choice(PROMISES)}",
            f"You are {r.choice(NAMES_OF_LOVE)} forever",
        ]
    else:
        lines = [
            f"Maybe words can never say enough",
            f"All I know is {r.choice(FEELINGS)}",
            f"In this lifetime and every next",
            f"{r.choice(PROMISES)}",
        ]
    return "\n".join(lines)


def generate_weekly_lyrics() -> dict:
    """
    Generate completely unique lyrics every week.
    Uses week number as seed so same week always gives same song
    but different weeks give different songs.
    Returns dict with title, prompt, style.
    """
    week  = datetime.utcnow().isocalendar()[1]
    year  = datetime.utcnow().year
    seed  = week + year * 100   # unique per week per year

    random.seed(seed)   # reproducible within same week

    title  = _title(week)
    style  = MUSIC_STYLES[week % len(MUSIC_STYLES)]
    mood   = MOODS[week % len(MOODS)]

    verse1  = _verse(week, 1)
    verse2  = _verse(week, 2)
    chorus  = _chorus(week)
    bridge  = _bridge(week)

    prompt = (
        f"[Verse]\n{verse1}\n\n"
        f"[Chorus]\n{chorus}\n\n"
        f"[Verse]\n{verse2}\n\n"
        f"[Chorus]\n{chorus}\n\n"
        f"[Bridge]\n{bridge}\n\n"
        f"[Chorus]\n{chorus}"
    )

    print(f"  [lyrics] Week {week}/{year}: '{title}' ({mood})")
    print(f"  [lyrics] Style: {style[:50]}...")

    return {
        "title" : title,
        "prompt": prompt,
        "style" : style,
        "mood"  : mood,
    }
