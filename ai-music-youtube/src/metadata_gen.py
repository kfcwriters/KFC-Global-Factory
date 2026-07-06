"""
Generates a YouTube title, description, and tags for the day's video.

Uses the Claude API if ANTHROPIC_API_KEY is set (better, more varied
titles); otherwise falls back to a simple template so the pipeline
always works even with zero paid keys.
"""
import os
import json
import requests

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def _template_metadata(niche_name: str) -> dict:
    title = f"{niche_name.title()} | Relaxing Music for Focus & Calm"
    description = (
        f"Enjoy this relaxing {niche_name} track — perfect for background focus, "
        "unwinding, or a peaceful moment in your day.\n\n"
        "Subscribe for daily calming music.\n\n"
        "This video features AI-assisted music and visuals."
    )
    tags = [niche_name, "relaxing music", "ambient music", "calm music", "focus music"]
    return {"title": title, "description": description, "tags": tags}


def generate_metadata(niche_name: str) -> dict:
    if not ANTHROPIC_API_KEY:
        return _template_metadata(niche_name)

    prompt = f"""Write a YouTube title, description, and 5 tags for a relaxing
ambient/instrumental music video in the niche: "{niche_name}".

Return ONLY valid JSON, no markdown, in this exact shape:
{{"title": "...", "description": "...", "tags": ["...", "..."]}}

Rules:
- Title under 90 characters, appealing but not clickbait, no ALL CAPS spam.
- Description: 2-3 short sentences, warm tone, end with a one-line note that
  this video features AI-assisted music and visuals.
- 5 relevant tags as short lowercase phrases.
"""
    try:
        resp = requests.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        text = resp.json()["content"][0]["text"].strip()
        if text.startswith("```"):
            text = text.split("```")[1].replace("json", "", 1).strip()
        return json.loads(text)
    except Exception as e:
        print(f"  Claude metadata generation failed ({e}), using template.")
        return _template_metadata(niche_name)


if __name__ == "__main__":
    print(generate_metadata("thyroid health music"))
