"""
shorts_maker.py
Converts a landscape music video into a vertical YouTube Short.
Takes the most engaging 45-60 second clip and reformats to 9:16.
"""
import subprocess, os


def make_short_from_video(source_video: str, output_path: str,
                          duration: int = 55, start_offset: int = 15) -> str:
    """
    Extract a vertical Short from an existing landscape video.

    Args:
        source_video : Path to the full landscape MP4.
        output_path  : Where to save the vertical short.
        duration     : Length of the short in seconds (max 60 for Shorts).
        start_offset : Seconds into the source video to start the clip
                       (skip the intro/title card for a stronger hook).

    Returns:
        output_path
    """
    print(f"  [shorts] Extracting {duration}s clip from {start_offset}s mark ...")

    # Crop landscape (1280x720) to vertical (720x1280) with center crop,
    # then scale to standard Shorts resolution 1080x1920
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_offset),
        "-i", source_video,
        "-t", str(duration),
        "-vf",
        "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos,"
        "eq=contrast=1.08:saturation=1.15",   # slightly punchier for mobile
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"FFmpeg Shorts export failed:\n{r.stderr[-500:]}")

    size = os.path.getsize(output_path) // 1024
    print(f"  [shorts] Short created: {size} KB ✓")
    return output_path


def make_shorts_metadata(original_title: str, tags: list) -> dict:
    """Build Shorts-specific title/description with #Shorts tag."""
    # Shorts titles should be punchy and include #Shorts
    short_title = original_title.replace("|", "-")[:90] + " #Shorts"

    short_desc = (
        f"{original_title}\n\n"
        f"🎵 Full song on our channel!\n"
        f"🔔 Subscribe for daily music Shorts\n\n"
        f"#Shorts #shortsvideo #viral " +
        " ".join(f"#{t.replace(' ','')}" for t in tags[:5])
    )

    short_tags = ["shorts", "short"] + tags[:13]

    return {
        "title": short_title[:100],
        "description": short_desc[:5000],
        "tags": short_tags[:15],
    }
