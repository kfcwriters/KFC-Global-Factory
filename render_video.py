import subprocess
import sys

ffmpeg_cmd = [
    "ffmpeg",
    "-y",
    "-loglevel", "error",          # prevent huge logs (CRITICAL)
    "-stats",                      # lightweight progress
    "-f","lavfi",
    "-i","color=c=#0b1d3a:s=1920x1080:r=30",
    "-i","voice.mp3",
    "-vf","subtitles=subtitles.srt:force_style="
          "'FontName=Arial,FontSize=78,PrimaryColour=&HFFFFFF&,"
          "OutlineColour=&H000000&,BorderStyle=1,Outline=3,Alignment=2,MarginV=60'",
    "-t","300",
    "-shortest",
    "-c:v","libx264",
    "-preset","ultrafast",     # VERY IMPORTANT for CI runners
    "-pix_fmt","yuv420p",
    "-movflags","+faststart",
    "final_video.mp4"
]

process = subprocess.Popen(
    ffmpeg_cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# 🔥 THIS LOOP PREVENTS GITHUB FREEZE
for line in process.stdout:
    sys.stdout.write(line)

process.wait()

if process.returncode != 0:
    raise RuntimeError("FFmpeg render failed")

print("Video render complete.")
