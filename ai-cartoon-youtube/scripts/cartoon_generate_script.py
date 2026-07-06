"""
Step 1: Generate a children's story script split into scenes.

Uses Groq's free API (https://console.groq.com) — sign up free,
create an API key, no credit card required as of writing.

Output: a JSON list of scenes, each with:
  - narration: the text to be spoken (TTS)
  - image_prompt: the visual description for that scene
"""
import os
import json
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "config"))
from cartoon_config import EPISODE_LENGTH_SCENES, ART_STYLE

GROQ_API_KEY_CARTOON = os.environ.get("GROQ_API_KEY_CARTOON")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # free-tier model on Groq as of writing


def build_prompt(topic: str) -> str:
    return f"""You are writing a short, gentle children's cartoon episode (ages 3-7) about: {topic}

Write exactly {EPISODE_LENGTH_SCENES} scenes. Return ONLY valid JSON (no markdown, no commentary),
as a list like this:

[
  {{
    "narration": "One or two simple, warm sentences a narrator would say, for a young child.",
    "image_prompt": "A short visual description of what's on screen in this scene, focused on characters and setting, no text in the image."
  }}
]

Rules:
- Keep language extremely simple, positive, and age-appropriate.
- No violence, no scary content, no sensitive themes.
- Keep the same main character(s) and setting across all scenes for visual consistency.
- Each image_prompt should clearly describe the character(s) appearance every time (e.g. "a small orange fox with a blue scarf") so an image generator draws them consistently.
- Story should have a clear beginning, a small simple problem, and a kind resolution with a gentle lesson.
"""


def generate_script(topic: str) -> list:
    if not GROQ_API_KEY_CARTOON:
        raise RuntimeError("GROQ_API_KEY_CARTOON environment variable is not set.")

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": build_prompt(topic)}],
        "temperature": 0.9,
    }
    req = urllib.request.Request(
        GROQ_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY_CARTOON}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    text = data["choices"][0]["message"]["content"].strip()
    # Models sometimes wrap JSON in ```json fences despite instructions — strip them.
    if text.startswith("```"):
        text = text.split("```")[1]
        text = text.replace("json", "", 1).strip()

    scenes = json.loads(text)

    # Append the fixed art style to every image prompt for visual consistency.
    for scene in scenes:
        scene["image_prompt"] = f'{scene["image_prompt"]}, {ART_STYLE}'

    return scenes


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "a fox who learns to share"
    scenes = generate_script(topic)
    out_path = os.path.join(os.path.dirname(__file__), "..", "cartoon_output", "script.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(scenes, f, indent=2)
    print(f"Wrote {len(scenes)} scenes to {out_path}")
