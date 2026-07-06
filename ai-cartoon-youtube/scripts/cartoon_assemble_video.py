"""
Step 4: Assemble the final video from images + audio using ffmpeg.

For each scene:
  - Measures the narration audio duration.
  - Applies a slow "Ken Burns" zoom/pan to the still image for that
    exact duration (so it feels animated, not a static slideshow).
  - Attaches that scene's narration audio.
Then concatenates all scenes into one final .mp4.

Requires ffmpeg + ffprobe installed on the runner (GitHub's ubuntu-latest
runners have both preinstalled).
"""
import os
import sys
import json
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "config"))
from cartoon_config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS, KEN_BURNS_ZOOM, CHANNEL_NAME


def get_audio_duration(path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return float(result.stdout.strip())


def build_scene_clip(image_path: str, audio_path: str, out_path: str, duration: float):
    total_frames = int(duration * FPS)
    # zoompan filter: slowly zooms from 1.0 to KEN_BURNS_ZOOM over the clip
    zoom_expr = f"min(zoom+{(KEN_BURNS_ZOOM - 1) / max(total_frames, 1):.6f},{KEN_BURNS_ZOOM})"
    vf = (
        f"scale={VIDEO_WIDTH*2}:{VIDEO_HEIGHT*2},"
        f"zoompan=z='{zoom_expr}':d={total_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest",
        "-t", str(duration),
        out_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def concatenate_clips(clip_paths: list, out_path: str):
    list_file = os.path.join(os.path.dirname(out_path), "concat_list.txt")
    with open(list_file, "w") as f:
        for p in clip_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", out_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def assemble_video(script_path: str, out_dir: str, final_out_path: str):
    with open(script_path) as f:
        scenes = json.load(f)

    os.makedirs(out_dir, exist_ok=True)
    clip_paths = []
    for i, scene in enumerate(scenes):
        print(f"Rendering scene {i+1}/{len(scenes)}...")
        duration = get_audio_duration(scene["audio_path"])
        clip_path = os.path.join(out_dir, f"clip_{i:02d}.mp4")
        build_scene_clip(scene["image_path"], scene["audio_path"], clip_path, duration)
        clip_paths.append(clip_path)

    print("Concatenating scenes...")
    concatenate_clips(clip_paths, final_out_path)
    print(f"Final video saved to {final_out_path}")


if __name__ == "__main__":
    base = os.path.join(os.path.dirname(__file__), "..", "cartoon_output")
    assemble_video(
        script_path=os.path.join(base, "script.json"),
        out_dir=os.path.join(base, "clips"),
        final_out_path=os.path.join(base, "final_episode.mp4"),
    )
