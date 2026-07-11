"""
video_assembly_kenburns.py — EXPERIMENTAL (Kids pipeline testing only)
========================================================================
Ken Burns zoom/pan effect + multi-style crossfade transitions.
Separate from video_assembly.py (used by song pipelines) so the
proven, stable song pipeline is never affected by this experiment.

If this tests well on the kids channel, we can promote it to
video_assembly.py for the song pipelines later.
"""
import os, subprocess


def create_video(audio_path: str, image_paths: list,
                 output_path: str, vertical: bool = False) -> str:
    TARGET_W = 1080 if vertical else 1280
    TARGET_H = 1920 if vertical else 720
    FPS      = 30
    FADE_SEC = 1.2

    n = len(image_paths)
    if n == 0:
        raise ValueError("No images provided")

    duration     = _probe_duration(audio_path)
    secs_per_img = duration / n
    print(f"  [video-kb] {n} images × {secs_per_img:.1f}s = {duration:.1f}s total")
    print(f"  [video-kb] format: {'vertical 1080x1920' if vertical else 'landscape 1280x720'}")
    print(f"  [video-kb] Ken Burns zoom/pan + crossfade transitions (EXPERIMENTAL)")

    try:
        _build_with_kenburns(audio_path, image_paths, output_path,
                             secs_per_img, duration, TARGET_W, TARGET_H,
                             FADE_SEC, FPS)
    except Exception as e:
        print(f"  [video-kb] Ken Burns failed ({e}) — falling back to simple crossfade")
        _build_simple_fallback(audio_path, image_paths, output_path,
                              secs_per_img, duration, TARGET_W, TARGET_H, FADE_SEC)

    size_mb = os.path.getsize(output_path) / 1_048_576
    print(f"  [video-kb] saved {output_path} ({size_mb:.1f} MB)")
    return output_path


def _probe_duration(path: str) -> float:
    cmd = ["ffprobe", "-v", "error",
           "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", path]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


PAN_DIRECTIONS = [
    "zoom_in_center", "zoom_in_topleft", "zoom_in_topright",
    "zoom_in_bottomleft", "zoom_in_bottomright", "zoom_out_center",
    "pan_left_to_right", "pan_right_to_left",
]


def _kenburns_filter(idx: int, w: int, h: int, dur: float, fps: int) -> str:
    direction = PAN_DIRECTIONS[idx % len(PAN_DIRECTIONS)]
    total_frames = int(dur * fps)

    oversample_w = int(w * 1.3)
    oversample_h = int(h * 1.3)

    zoom_end = 1.15
    x_expr, y_expr = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"

    if direction == "zoom_in_center":
        z_expr = f"min(zoom+0.0009,{zoom_end})"
    elif direction == "zoom_in_topleft":
        z_expr = f"min(zoom+0.0009,{zoom_end})"
        x_expr, y_expr = "0", "0"
    elif direction == "zoom_in_topright":
        z_expr = f"min(zoom+0.0009,{zoom_end})"
        x_expr, y_expr = "iw-iw/zoom", "0"
    elif direction == "zoom_in_bottomleft":
        z_expr = f"min(zoom+0.0009,{zoom_end})"
        x_expr, y_expr = "0", "ih-ih/zoom"
    elif direction == "zoom_in_bottomright":
        z_expr = f"min(zoom+0.0009,{zoom_end})"
        x_expr, y_expr = "iw-iw/zoom", "ih-ih/zoom"
    elif direction == "zoom_out_center":
        z_expr = f"if(eq(on,0),{zoom_end},max(zoom-0.0009,1.0))"
    elif direction == "pan_left_to_right":
        z_expr = "1.12"
        x_expr = f"(iw-iw/zoom)*(on/{total_frames})"
        y_expr = "ih/2-(ih/zoom/2)"
    else:
        z_expr = "1.12"
        x_expr = f"(iw-iw/zoom)*(1-on/{total_frames})"
        y_expr = "ih/2-(ih/zoom/2)"

    return (
        f"scale={oversample_w}:{oversample_h}:force_original_aspect_ratio=increase,"
        f"crop={oversample_w}:{oversample_h},"
        f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':"
        f"d={total_frames}:s={w}x{h}:fps={fps}"
    )


def _build_with_kenburns(audio_path, image_paths, output_path,
                         secs_per_img, total_dur, w, h, fade, fps):
    n = len(image_paths)
    clip_dur = secs_per_img + fade

    inputs = []
    for img in image_paths:
        inputs += ["-loop", "1", "-t", str(clip_dur), "-i", img]
    inputs += ["-i", audio_path]

    filter_parts = []
    for i in range(n):
        kb_filter = _kenburns_filter(i, w, h, clip_dur, fps)
        filter_parts.append(f"[{i}:v]{kb_filter},format=yuv420p[v{i}]")

    prev_label = "v0"
    transitions = ["fade", "wipeleft", "wiperight", "slideup", "slidedown",
                   "circleopen", "dissolve", "smoothleft"]

    for i in range(1, n):
        offset = secs_per_img * i - fade * (i - 1)
        next_label = f"xf{i}" if i < n - 1 else "outv"
        trans = transitions[i % len(transitions)]
        filter_parts.append(
            f"[{prev_label}][v{i}]xfade=transition={trans}:"
            f"duration={fade}:offset={offset:.3f}[{next_label}]"
        )
        prev_label = next_label

    if n == 1:
        filter_parts = [f"[0:v]{_kenburns_filter(0, w, h, total_dur, fps)}[outv]"]

    filter_complex = ";".join(filter_parts)
    audio_index = n

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", f"{audio_index}:a",
        "-t", str(total_dur),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    print("  [video-kb] rendering with Ken Burns + transitions ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Ken Burns render failed:\n{result.stderr[-800:]}")


def _build_simple_fallback(audio_path, image_paths, output_path,
                           secs_per_img, total_dur, w, h, fade):
    n = len(image_paths)
    scale_crop = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"

    inputs = []
    for img in image_paths:
        inputs += ["-loop", "1", "-t", str(secs_per_img + fade), "-i", img]
    inputs += ["-i", audio_path]

    filter_parts = [f"[{i}:v]{scale_crop}[v{i}]" for i in range(n)]
    prev_label = "v0"
    for i in range(1, n):
        offset = secs_per_img * i - fade * (i - 1)
        next_label = f"xf{i}" if i < n - 1 else "outv"
        filter_parts.append(
            f"[{prev_label}][v{i}]xfade=transition=fade:"
            f"duration={fade}:offset={offset:.3f}[{next_label}]"
        )
        prev_label = next_label

    if n == 1:
        filter_parts = [f"[0:v]{scale_crop}[outv]"]

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", ";".join(filter_parts),
        "-map", "[outv]", "-map", f"{n}:a",
        "-t", str(total_dur),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", "-pix_fmt", "yuv420p",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg fallback also failed:\n{result.stderr[-1000:]}")
    print("  [video-kb] fallback render succeeded ✓")
