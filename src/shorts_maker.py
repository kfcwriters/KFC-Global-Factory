"""
shorts_maker.py
Extracts a 55-second vertical Short from the main landscape video.
"""
import subprocess, os


def make_short_from_video(input_path: str, output_path: str,
                          duration: int = 55, start_offset: int = 15) -> str:
    """Extract a 55s vertical clip from landscape video."""
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_offset),
        "-i", input_path,
        "-t", str(duration),
        "-vf", "crop=ih*9/16:ih,scale=1080:1920",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Shorts creation failed: {result.stderr[-300:]}")

    size_kb = os.path.getsize(output_path) // 1024
    print(f"  [shorts] Short created: {size_kb} KB ✓")
    return output_path


def make_short_from_video_vertical(input_path: str, output_path: str,
                                   duration: int = 55, start_offset: int = 15) -> str:
    """Extract from already-vertical video."""
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_offset),
        "-i", input_path,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Shorts creation failed: {result.stderr[-300:]}")

    size_kb = os.path.getsize(output_path) // 1024
    print(f"  [shorts] Short created: {size_kb} KB ✓")
    return output_path


def make_shorts_metadata(title: str, tags: list,
                         is_hindi: bool = False) -> dict:
    """Generate Shorts-optimized metadata."""
    from seo_gen import make_shorts_seo
    return make_shorts_seo(title, is_hindi=is_hindi)
