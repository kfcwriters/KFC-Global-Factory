"""
clip_stitcher.py
Stitches multiple short AI-generated video clips into one video,
with audio overlay (narration + music) synced across all clips.
"""
import os, subprocess, tempfile
from pathlib import Path


def stitch_clips(clip_bytes_list: list, audio_path: str,
                 output_path: str, target_duration: int = 180,
                 vertical: bool = False) -> str:
    """
    Combine multiple short video clips into one continuous video,
    then overlay the audio track. Loops clips if needed to fill duration.
    """
    if not clip_bytes_list:
        raise ValueError("No clips provided to stitch")

    W, H = (1080, 1920) if vertical else (1280, 720)

    with tempfile.TemporaryDirectory(prefix="stitch_") as tmp:
        tmp = Path(tmp)

        clip_paths = []
        for i, clip_bytes in enumerate(clip_bytes_list):
            p = tmp / f"clip_{i:02d}.mp4"
            p.write_bytes(clip_bytes)
            clip_paths.append(str(p))

        print(f"  [stitch] Normalizing + combining {len(clip_paths)} clips ...")

        concat_file = tmp / "concat.txt"
        with open(concat_file, "w") as f:
            for p in clip_paths:
                norm_path = p.replace(".mp4", "_norm.mp4")
                _normalize_clip(p, norm_path, W, H)
                f.write(f"file '{norm_path}'\n")

        combined = str(tmp / "combined.mp4")
        r = subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file), "-c", "copy", combined
        ], capture_output=True, text=True)

        if r.returncode != 0:
            print(f"  [stitch] concat copy failed, re-encoding ...")
            r = subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                combined
            ], capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError(f"Stitching failed: {r.stderr[-500:]}")

        print(f"  [stitch] Adding audio track (target {target_duration}s) ...")
        r2 = subprocess.run([
            "ffmpeg", "-y",
            "-stream_loop", "-1", "-i", combined,
            "-i", audio_path,
            "-map", "0:v", "-map", "1:a",
            "-t", str(target_duration),
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            "-pix_fmt", "yuv420p",
            output_path
        ], capture_output=True, text=True)

        if r2.returncode != 0:
            raise RuntimeError(f"Audio overlay failed: {r2.stderr[-500:]}")

    size = os.path.getsize(output_path) // 1024
    print(f"  [stitch] Final video: {size} KB ✓")
    return output_path


def _normalize_clip(input_path: str, output_path: str, width: int, height: int):
    r = subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,"
               f"crop={width}:{height},fps=24",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-an",
        output_path
    ], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Normalize failed: {r.stderr[-300:]}")
