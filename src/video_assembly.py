"""
video_assembly.py
Assembles images + audio into MP4 using FFmpeg.
Supports landscape (1280x720) and vertical/Shorts (1080x1920) modes.
"""
import os, subprocess


def create_video(audio_path: str, image_paths: list,
                 output_path: str, vertical: bool = False) -> str:
    """
    Args:
        audio_path  : Path to audio file.
        image_paths : Ordered list of image file paths.
        output_path : Destination .mp4 path.
        vertical    : True = 1080x1920 (Shorts), False = 1280x720 (landscape).
    """
    TARGET_W = 1080 if vertical else 1280
    TARGET_H = 1920 if vertical else 720
    FPS      = 24
    FADE_SEC = 1.5

    n = len(image_paths)
    if n == 0:
        raise ValueError("No images provided")

    duration    = _probe_duration(audio_path)
    secs_per_img = duration / n
    print(f"  [video] {n} images × {secs_per_img:.1f}s = {duration:.1f}s total")
    print(f"  [video] format: {'vertical 1080x1920' if vertical else 'landscape 1280x720'}")

    _build_with_ffmpeg(audio_path, image_paths, output_path,
                       secs_per_img, duration, TARGET_W, TARGET_H, FADE_SEC)

    size_mb = os.path.getsize(output_path) / 1_048_576
    print(f"  [video] saved {output_path} ({size_mb:.1f} MB)")
    return output_path


def _probe_duration(path: str) -> float:
    cmd = ["ffprobe", "-v", "error",
           "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", path]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def _build_with_ffmpeg(audio_path, image_paths, output_path,
                       secs_per_img, total_dur, w, h, fade):
    n = len(image_paths)

    inputs = []
    for img in image_paths:
        inputs += ["-loop", "1", "-t", str(secs_per_img + fade), "-i", img]
    inputs += ["-i", audio_path]

    scale_crop = (
        f"scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h}"
    )

    filter_parts = []
    for i in range(n):
        filter_parts.append(f"[{i}:v]{scale_crop}[v{i}]")

    prev_label = "v0"
    for i in range(1, n):
        offset     = secs_per_img * i - fade * (i - 1)
        next_label = f"xf{i}" if i < n - 1 else "outv"
        filter_parts.append(
            f"[{prev_label}][v{i}]xfade=transition=fade:"
            f"duration={fade}:offset={offset:.3f}[{next_label}]"
        )
        prev_label = next_label

    if n == 1:
        filter_parts = [f"[0:v]{scale_crop}[outv]"]

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", ";".join(filter_parts),
        "-map", "[outv]",
        "-map", f"{n}:a",
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
