"""
video_assembly.py
Assembles a list of images + an audio file into an MP4 video
with smooth crossfade transitions.
"""

import os
import subprocess
import tempfile
from pathlib import Path


TARGET_W  = 1280
TARGET_H  = 720
FPS       = 24
FADE_SEC  = 1.5     # crossfade duration


def create_video(audio_path: str, image_paths: list[str], output_path: str) -> str:
    """
    Build an MP4 from images + audio.

    Strategy: use FFmpeg directly via subprocess for speed and reliability
    on headless CI runners (avoids moviepy's heavier dependency chain).

    Args:
        audio_path  : Path to audio file (wav/flac/mp3).
        image_paths : Ordered list of image file paths.
        output_path : Destination .mp4 path.

    Returns:
        output_path on success.
    """
    n = len(image_paths)
    if n == 0:
        raise ValueError("No images provided to create_video()")

    # Probe audio duration
    duration = _probe_duration(audio_path)
    secs_per_image = duration / n

    print(f"  [video] {n} images × {secs_per_image:.1f}s = {duration:.1f}s total")

    # Build FFmpeg filter graph for crossfades
    # Each image shown for secs_per_image, faded into the next
    _build_with_ffmpeg(audio_path, image_paths, output_path,
                       secs_per_image, duration)

    size_mb = os.path.getsize(output_path) / 1_048_576
    print(f"  [video] saved {output_path} ({size_mb:.1f} MB)")
    return output_path


# ─────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────

def _probe_duration(path: str) -> float:
    """Use ffprobe to get audio duration in seconds."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def _build_with_ffmpeg(audio_path, image_paths, output_path,
                       secs_per_img, total_dur):
    """
    Construct and run a single FFmpeg command that:
      1. Reads each image as a looped still for secs_per_img seconds.
      2. Scales/crops to TARGET_W × TARGET_H.
      3. Applies xfade transitions between consecutive clips.
      4. Mixes in the audio track.
    """
    n = len(image_paths)

    # Build inputs: one -loop 1 -t <dur> -i <file> per image
    inputs = []
    for img in image_paths:
        inputs += ["-loop", "1", "-t", str(secs_per_img + FADE_SEC), "-i", img]
    # Audio input last
    inputs += ["-i", audio_path]

    # Scale/crop filter for each stream
    scale_crop = (
        f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,"
        f"crop={TARGET_W}:{TARGET_H}"
    )

    filter_parts = []
    # Label each video stream after scale/crop
    for i in range(n):
        filter_parts.append(f"[{i}:v]{scale_crop}[v{i}]")

    # Chain xfades
    prev_label = "v0"
    for i in range(1, n):
        offset = secs_per_img * i - FADE_SEC * (i - 1)
        next_label = f"xf{i}" if i < n - 1 else "outv"
        filter_parts.append(
            f"[{prev_label}][v{i}]xfade=transition=fade:"
            f"duration={FADE_SEC}:offset={offset:.3f}[{next_label}]"
        )
        prev_label = next_label

    if n == 1:
        # Only one image — no xfade needed
        filter_parts = [f"[0:v]{scale_crop}[outv]"]

    filter_complex = ";".join(filter_parts)
    audio_index = n  # audio is the last input

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", f"{audio_index}:a",
        "-t", str(total_dur),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    print("  [video] running ffmpeg …")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{result.stderr[-1000:]}")
