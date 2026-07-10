"""
seo_gen.py
High-converting YouTube SEO generator — NO API needed, pure Python.
"""
import random

TITLE_PATTERNS = {
    "romantic songs": [
        "{song_title} 🎵 Beautiful Romantic Love Song 2026",
        "{song_title} | Emotional Love Song With Lyrics 🌹",
        "{song_title} - Romantic Ballad For Someone Special 💕",
        "New Romantic Song 2026: {song_title} 🎶",
        "{song_title} 🎧 Sad + Romantic Love Song",
        "{song_title} | AI Music Cover | Emotional Ballad",
        "Best Romantic Song 2026 - {song_title} 🌹",
        "{song_title} 💖 Love Song That Will Make You Cry",
    ],
    "lofi study music": [
        "3 Hours Lofi Study Music 🎧 Deep Focus Beats",
        "Lofi Hip Hop Radio 🎵 Chill Beats To Study/Relax To",
        "Study Music For Concentration 📚 Lofi Focus Beats",
        "1 Hour Lofi Music For Studying 🌙 Calm Study Beats",
    ],
    "meditation music": [
        "10 Minute Meditation Music 🧘 Deep Relaxation",
        "Healing Meditation Music 🌿 Stress Relief & Anxiety",
        "Peaceful Meditation Music For Sleep & Yoga 🙏",
    ],
    "sleep music": [
        "8 Hours Deep Sleep Music 😴 Relaxing Sleep Sounds",
        "Fall Asleep Fast 🌙 Calming Sleep Music",
        "Sleep Music For Insomnia 💤 Peaceful Night Sounds",
    ],
    "focus work music": [
        "2 Hours Deep Focus Music 🎯 Study & Work Concentration",
        "Productivity Music For Work 💼 Focus & Concentration",
    ],
    "healing music": [
        "432Hz Healing Frequency 🎵 Full Body Cell Regeneration",
        "528Hz Miracle Tone 💚 DNA Repair & Healing Music",
    ],
    "wellness music": [
        "Morning Wellness Music 🌅 Positive Energy Start",
        "Yoga Music For Wellness & Mindfulness 🧘‍♀️",
    ],
}

DEFAULT_PATTERNS = [
    "{song_title} 🎵 Relaxing Music 2026",
    "New Music 2026: {song_title} 🎶",
]

EMOJI_SETS = {
    "romantic songs"    : ["🌹","💕","💖","🎵","💝","🥀","💗"],
    "lofi study music"  : ["🎧","📚","🌙","☕","💻"],
    "meditation music"  : ["🧘","🙏","🌿","✨","☮️"],
    "sleep music"       : ["😴","🌙","💤","⭐","🌌"],
    "focus work music"  : ["🎯","💼","🧠","📖","💻"],
    "healing music"     : ["💚","🌿","✨","🔮","🧘"],
    "wellness music"    : ["🌸","💚","🌿","🌅","🧘‍♀️"],
}

HASHTAG_BANKS = {
    "romantic songs": ["#romanticsongs","#lovesongs","#romanticmusic","#lovesong2026",
                       "#emotionalsong","#sadlovesongs","#heartbrokensongs","#aimusic"],
    "lofi study music": ["#lofi","#lofihiphop","#studymusic","#chillbeats","#lofibeats"],
    "meditation music": ["#meditation","#meditationmusic","#mindfulness","#healingmusic"],
    "sleep music": ["#sleepmusic","#deepsleep","#relaxingmusic","#insomnia"],
    "focus work music": ["#focusmusic","#deepwork","#productivity","#studymusic"],
    "healing music": ["#healingfrequency","#432hz","#528hz","#soundhealing"],
    "wellness music": ["#wellnessmusic","#selfcare","#mindfulness","#wellness"],
}


def make_title(song_title: str, niche: str) -> str:
    patterns = TITLE_PATTERNS.get(niche, DEFAULT_PATTERNS)
    pattern  = random.choice(patterns)
    return pattern.format(song_title=song_title)[:100]


def make_description(song_title: str, niche: str, music_style: str = "") -> str:
    emoji_set   = EMOJI_SETS.get(niche, ["🎵","🎶","✨"])
    e1, e2, e3  = random.sample(emoji_set, min(3, len(emoji_set)))
    niche_read  = niche.replace("_"," ").title()
    hashtags    = HASHTAG_BANKS.get(niche, ["#music","#aimusic"])
    tag_line    = " ".join(hashtags[:8])

    opening = (f"{e1} {song_title} — {niche_read} to help you relax, "
              f"unwind and feel better. Perfect background music for any moment.\n\n")
    body = (f"{e2} About This Track:\n{song_title} is a beautiful "
           f"{niche_read.lower()} track designed to bring you peace, "
           f"comfort and emotional connection.\n\n"
           f"{e3} Perfect For:\n✔️ Relaxation and stress relief\n"
           f"✔️ Studying and deep focus\n✔️ Sleep and meditation\n"
           f"✔️ Background music while working\n"
           f"✔️ Emotional moments and reflection\n\n")
    if music_style:
        body += f"🎼 Style: {music_style}\n\n"
    timestamps = ("⏱️ Timestamps:\n00:00 Intro\n00:30 Main Theme\n"
                 "02:00 Emotional Build\n03:00 Outro\n\n")
    cta = (f"🔔 SUBSCRIBE for new {niche_read.lower()} every week!\n"
          f"👍 LIKE if this touched your heart\n💬 COMMENT your thoughts below\n\n")
    disclaimer = "🎹 This track was composed using AI music technology.\n\n"

    return (opening+body+timestamps+cta+disclaimer+tag_line)[:5000]


def make_tags(song_title: str, niche: str) -> list:
    song_words = [w.lower() for w in song_title.split() if len(w)>3][:3]

    broad = {
        "romantic songs": ["romantic songs","love songs","romantic music",
                           "love song 2026","emotional songs","sad love songs"],
        "lofi study music": ["lofi","lofi hip hop","study music","chill beats"],
        "meditation music": ["meditation music","meditation","mindfulness","healing music"],
        "sleep music": ["sleep music","deep sleep","relaxing music","sleep sounds"],
        "focus work music": ["focus music","study music","productivity music"],
        "healing music": ["healing music","432hz","528hz","sound healing"],
        "wellness music": ["wellness music","self care music","yoga music"],
    }.get(niche, ["music","relaxing music"])

    long_tail = {
        "romantic songs": ["best romantic song 2026","new love song","sad romantic song"],
        "lofi study music": ["lofi radio 24/7","study with me music"],
        "meditation music": ["10 minute meditation","stress relief music"],
        "sleep music": ["8 hour sleep music","fall asleep fast"],
        "focus work music": ["binaural beats focus"],
        "healing music": ["432hz frequency music"],
        "wellness music": ["morning wellness music"],
    }.get(niche, [])

    tags = broad + long_tail + song_words + ["ai music","no copyright music"]
    seen, result = set(), []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower()); result.append(t)
    return result[:15]


def generate_seo(song_title: str, niche: str, music_style: str = "") -> dict:
    return {
        "title"      : make_title(song_title, niche),
        "description": make_description(song_title, niche, music_style),
        "tags"       : make_tags(song_title, niche),
    }
