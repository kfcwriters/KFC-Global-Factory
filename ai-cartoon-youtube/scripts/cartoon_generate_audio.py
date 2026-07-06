"""
Step 3: Generate narration audio for each scene using edge-tts
(free, no API key — uses Microsoft Edge's online text-to-speech).

Install: pip install edge-tts
"""
import os
import sys
import json
import asyncio
import edge_tts

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "config"))
from cartoon_config import TTS_VOICE


async def generate_audio_for_scene(text: str, out_path: str):
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    await communicate.save(out_path)


async def generate_all_audio(script_path: str, out_dir: str):
    with open(script_path) as f:
        scenes = json.load(f)

    os.makedirs(out_dir, exist_ok=True)
    for i, scene in enumerate(scenes):
        out_path = os.path.join(out_dir, f"scene_{i:02d}.mp3")
        print(f"Generating audio {i+1}/{len(scenes)}...")
        await generate_audio_for_scene(scene["narration"], out_path)
        scene["audio_path"] = out_path

    with open(script_path, "w") as f:
        json.dump(scenes, f, indent=2)

    print(f"All {len(scenes)} audio clips saved to {out_dir}")


if __name__ == "__main__":
    base = os.path.join(os.path.dirname(__file__), "..", "cartoon_output")
    asyncio.run(
        generate_all_audio(
            script_path=os.path.join(base, "script.json"),
            out_dir=os.path.join(base, "audio"),
        )
    )
