"""
Assembles the final video: takes the generated music track and 1+
background images, and builds a slow pan/zoom ("Ken Burns") visual
that lasts the full length of the music, using ffmpeg.

If multiple images are given, it splits the audio duration evenly
across them.
"""
import subprocess
import os


def get_audio_duration(path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return float(result.stdout.strip())


def _build_segment(image_path: str, duration: float, out_path: str,
                    width: int = 1280, height: int = 720, fps: int = 30, zoom_to: float = 1.12):
    total_frames = max(int(duration * fps), 1)
    zoom_step = (zoom_to - 1) / total_frames
    vf = (
        f"scale={width*2}:{height*2},"
        f"zoompan=z='min(zoom+{zoom_step:.6f},{zoom_to})':d={total_frames}:s={width}x{height}:fps={fps}"
    )
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", image_path,
        "-vf", vf, "-t", str(duration),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        out_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def assemble_video(image_paths: list, audio_path: str, out_path: str,
                    width: int = 1280, height: int = 720, fps: int = 30):
    total_duration = get_audio_duration(audio_path)
    per_image = total_duration / len(image_paths)

    tmp_dir = os.path.join(os.path.dirname(out_path), "tmp_segments")
    os.makedirs(tmp_dir, exist_ok=True)

    segment_paths = []
    for i, img_path in enumerate(image_paths):
        seg_path = os.path.join(tmp_dir, f"seg_{i:02d}.mp4")
        _build_segment(img_path, per_image, seg_path, width, height, fps)
        segment_paths.append(seg_path)

    # Concatenate visual segments
    list_file = os.path.join(tmp_dir, "concat_list.txt")
    with open(list_file, "w") as f:
        for p in segment_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    silent_video = os.path.join(tmp_dir, "video_only.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", silent_video],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )

    # Attach the music track
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", silent_video, "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac", "-shortest", out_path,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    print(f"Final video saved to {out_path}")


if __name__ == "__main__":
    assemble_video(["test_image.png"], "test_music.wav", "test_final.mp4")
