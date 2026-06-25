"""
metadata_gen.py
Generates YouTube title, description, and tags.
Primary : Claude API (claude-sonnet-4-6).
Fallback : deterministic template — works even without an API key.
"""

import json
import random
import re
import requests


CLAUDE_API = "https://api.anthropic.com/v1/messages"

EMOJIS = ["🎵", "🌙", "✨", "🎶", "🌊", "🔮", "🌿", "🎸", "🎹", "🌸", "💫", "🎼"]

HASHTAG_BANKS = {
    "lofi study music"  : ["#lofi", "#studymusic", "#lofihiphop", "#chillbeats", "#studywithme"],
    "meditation music"  : ["#meditation", "#mindfulness", "#healingmusic", "#zenmusic", "#calm"],
    "sleep music"       : ["#sleepmusic", "#deepsleep", "#relaxingmusic", "#insomnia", "#sleepaid"],
    "focus work music"  : ["#focusmusic", "#deepwork", "#productivity", "#flowstate", "#concentration"],
    "healing music"     : ["#healingfrequency", "#432hz", "#528hz", "#soundhealing", "#chakra"],
    "wellness music"    : ["#wellnessmusic", "#healthylife", "#metabolichealth", "#thyroid", "#hormones"],
}


def generate_metadata(music_prompt: str, niche: str,
                      anthropic_api_key: str | None = None) -> dict:
    """
    Return a dict with keys: title, description, tags (list[str]).
    """
    if anthropic_api_key:
        try:
            return _claude_metadata(music_prompt, niche, anthropic_api_key)
        except Exception as e:
            print(f"  [meta] Claude API error ({e}) — using template fallback")

    return _template_metadata(music_prompt, niche)


# ─────────────────────────────────────────
# Claude-powered path
# ─────────────────────────────────────────

def _claude_metadata(prompt: str, niche: str, api_key: str) -> dict:
    system = (
        "You are a YouTube SEO expert specialising in music channels. "
        "Return ONLY a valid JSON object — no markdown fences, no explanation. "
        "Keys: title (string ≤100 chars), description (string 250-350 words), "
        "tags (array of exactly 15 strings)."
    )
    user = (
        f"Create YouTube metadata for an AI-generated music video.\n"
        f"Music style: {prompt}\n"
        f"Channel niche: {niche}\n\n"
        "Requirements:\n"
        "- title: catchy, includes one emoji, ≤100 chars, contains the music style\n"
        "- description: engaging intro, 3-4 use-case bullet points, 00:00 timestamps, "
        "  5 relevant hashtags, call-to-action to subscribe\n"
        "- tags: mix of broad (lofi, study music) and specific (the exact music style)"
    )

    resp = requests.post(
        CLAUDE_API,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 1024,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
        timeout=30,
    )
    resp.raise_for_status()

    raw = resp.json()["content"][0]["text"].strip()
    # Strip any accidental markdown fences
    raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
    data = json.loads(raw)

    # Sanitise
    data["tags"] = [str(t).lstrip("#") for t in data.get("tags", [])][:15]
    return data


# ─────────────────────────────────────────
# Template fallback
# ─────────────────────────────────────────

def _template_metadata(prompt: str, niche: str) -> dict:
    e1, e2 = random.sample(EMOJIS, 2)
    style_words = " ".join(prompt.split()[:5]).title()

    title = f"{e1} {style_words} — AI Music {e2}"[:100]

    extra_tags = HASHTAG_BANKS.get(niche, [])
    tag_str    = "  ".join(extra_tags[:3])

    description = (
        f"{title}\n\n"
        f"Fully AI-generated {niche} — music and visuals created by artificial intelligence.\n\n"
        f"✅ Perfect for:\n"
        f"  • Studying and deep focus\n"
        f"  • Relaxation and stress relief\n"
        f"  • Background music while working\n"
        f"  • Meditation and mindfulness\n\n"
        f"🎵 Music style: {prompt.capitalize()}\n"
        f"🤖 Generated with AI music models\n"
        f"🎨 Visuals created with AI image generation\n\n"
        f"📌 Timestamps:\n"
        f"00:00 – Intro\n"
        f"00:30 – Main theme\n"
        f"02:00 – Variation\n"
        f"04:00 – Outro\n\n"
        f"🔔 Subscribe for daily AI music uploads!\n\n"
        f"#aimusic #artificialintelligence #{niche.replace(' ', '')} "
        f"#generativeai #relaxingmusic {tag_str}"
    )

    tags = [
        "ai music", "artificial intelligence music", "ai generated music",
        niche, "relaxing music", "study music", "ambient music",
        "chill music", "focus music", "lofi", "background music",
        "generative ai", "music ai", "instrumental", "no copyright music",
    ]

    return {
        "title"      : title,
        "description": description,
        "tags"       : tags[:15],
    }
