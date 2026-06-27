"""
metadata_gen.py
Primary : Claude API — tries multiple models.
Fallback: template — works without API key.
"""
import json, random, re, requests

CLAUDE_API = "https://api.anthropic.com/v1/messages"

CLAUDE_MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-3-5-haiku-20241022",
    "claude-3-haiku-20240307",
]

EMOJIS = ["🎵","🌙","✨","🎶","🌊","🔮","🌿","🎸","🎹","🌸","💫","🎼"]

HASHTAG_BANKS = {
    "romantic hindi english songs": ["#romanticsongs","#lovesongs","#bollywood","#romantic","#hindisongs"],
    "lofi study music"            : ["#lofi","#studymusic","#lofihiphop","#chillbeats","#studywithme"],
    "meditation music"            : ["#meditation","#mindfulness","#healingmusic","#zenmusic","#calm"],
    "sleep music"                 : ["#sleepmusic","#deepsleep","#relaxingmusic","#insomnia","#sleepaid"],
    "focus work music"            : ["#focusmusic","#deepwork","#productivity","#flowstate","#concentration"],
    "healing music"               : ["#healingfrequency","#432hz","#528hz","#soundhealing","#chakra"],
    "wellness music"              : ["#wellnessmusic","#healthylife","#metabolichealth","#thyroid","#hormones"],
}


def generate_metadata(music_prompt: str, niche: str,
                      anthropic_api_key: str | None = None) -> dict:
    if anthropic_api_key:
        try:
            return _claude_metadata(music_prompt, niche, anthropic_api_key)
        except Exception as e:
            print(f"  [meta] Claude failed ({e}) — using template")
    return _template_metadata(music_prompt, niche)


def _claude_metadata(prompt: str, niche: str, api_key: str) -> dict:
    system = (
        "You are a YouTube SEO expert for music channels. "
        "Return ONLY valid JSON — no markdown, no explanation. "
        'Keys: "title" (string, max 90 chars, 1 emoji), '
        '"description" (string, 200-300 words, include hashtags), '
        '"tags" (array of 15 strings, no # symbol).'
    )
    user = (
        f"YouTube metadata for a music video.\n"
        f"Music style: {prompt}\n"
        f"Niche: {niche}\n"
        "Make the title clickable and SEO-friendly."
    )
    headers = {
        "x-api-key"        : api_key,
        "anthropic-version": "2023-06-01",
        "content-type"     : "application/json",
    }
    last_error = None
    for model in CLAUDE_MODELS:
        try:
            resp = requests.post(
                CLAUDE_API, headers=headers,
                json={"model": model, "max_tokens": 800,
                      "system": system,
                      "messages": [{"role": "user", "content": user}]},
                timeout=30,
            )
            if resp.status_code == 200:
                raw  = resp.json()["content"][0]["text"].strip()
                raw  = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
                data = json.loads(raw)
                data["tags"] = [str(t).lstrip("#") for t in data.get("tags", [])][:15]
                print(f"  [meta] Claude OK (model={model}) ✓")
                return data
            print(f"  [meta] {model} → HTTP {resp.status_code}: {resp.text[:150]}")
            last_error = f"HTTP {resp.status_code}"
        except Exception as e:
            print(f"  [meta] {model} → {str(e)[:100]}")
            last_error = str(e)
    raise RuntimeError(f"All Claude models failed. Last: {last_error}")


def _template_metadata(prompt: str, niche: str) -> dict:
    e1, e2      = random.sample(EMOJIS, 2)
    style_words = " ".join(prompt.split()[:6]).title()
    title       = f"{e1} {style_words} — Music {e2}"[:90]
    extra_tags  = HASHTAG_BANKS.get(niche, [])
    tag_str     = "  ".join(extra_tags[:3])

    description = (
        f"{title}\n\n"
        f"Beautiful {niche} to relax, focus, and unwind.\n\n"
        f"Perfect for:\n"
        f"  Studying and deep focus\n"
        f"  Relaxation and stress relief\n"
        f"  Background music while working\n"
        f"  Meditation and sleep\n\n"
        f"Music style: {prompt.capitalize()}\n\n"
        f"Timestamps:\n"
        f"00:00 - Intro\n"
        f"00:30 - Main theme\n"
        f"02:00 - Variation\n"
        f"04:00 - Outro\n\n"
        f"Subscribe for daily music!\n\n"
        f"#Shorts #music #{niche.replace(' ', '')} #relaxingmusic {tag_str}"
    )

    tags = [
        "shorts", "music", niche, "relaxing music", "instrumental music",
        "background music", "study music", "sleep music", "meditation music",
        "ambient music", "chill music", "focus music", "calm music",
        "peaceful music", "no copyright music",
    ]

    return {"title": title, "description": description, "tags": tags[:15]}
