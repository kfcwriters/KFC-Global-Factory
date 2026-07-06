"""
Runs the entire pipeline end to end: script -> images -> audio -> video -> upload.

Usage:
  python cartoon_main.py "a fox who learns to share"
"""
import os
import sys
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
from cartoon_generate_script import generate_script
from cartoon_generate_images import generate_all_images
from cartoon_generate_audio import generate_all_audio
from cartoon_assemble_video import assemble_video
from cartoon_upload_youtube import upload_video

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "config"))
from cartoon_config import CHANNEL_NAME

import json

BASE = os.path.join(os.path.dirname(__file__), "cartoon_output")


def run(topic: str, do_upload: bool = True):
    os.makedirs(BASE, exist_ok=True)
    script_path = os.path.join(BASE, "script.json")

    print(f"\n=== 1/5: Generating script for: {topic} ===")
    scenes = generate_script(topic)
    with open(script_path, "w") as f:
        json.dump(scenes, f, indent=2)

    print("\n=== 2/5: Generating images ===")
    generate_all_images(script_path, os.path.join(BASE, "images"))

    print("\n=== 3/5: Generating narration audio ===")
    asyncio.run(generate_all_audio(script_path, os.path.join(BASE, "audio")))

    print("\n=== 4/5: Assembling video ===")
    final_path = os.path.join(BASE, "final_episode.mp4")
    assemble_video(script_path, os.path.join(BASE, "clips"), final_path)

    if do_upload:
        print("\n=== 5/5: Uploading to YouTube ===")
        upload_video(
            video_path=final_path,
            title=f"{topic.title()} | {CHANNEL_NAME}",
            description=(
                f"A gentle story for kids: {topic}\n\n"
                f"Subscribe to {CHANNEL_NAME} for more stories!\n\n"
                "This video was created with AI-assisted narration and illustration."
            ),
            tags=["kids cartoon", "children's story", "bedtime story", CHANNEL_NAME],
        )
    else:
        print("\nSkipping upload (do_upload=False). Video is ready at:", final_path)


if __name__ == "__main__":
    topic = sys.argv[1] if len(sys.argv) > 1 else "a fox who learns to share"
    upload_flag = "--no-upload" not in sys.argv
    run(topic, do_upload=upload_flag)
