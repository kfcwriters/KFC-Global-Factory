import subprocess

cmd = [
"ffmpeg",
"-f","lavfi",
"-i","color=c=#0b1d3a:s=1920x1080:r=30",  # animated background stream
"-i","voice.mp3",
"-vf",
"subtitles=subtitles.srt:force_style="
"'FontName=Arial,FontSize=78,PrimaryColour=&HFFFFFF&,"
"OutlineColour=&H000000&,BorderStyle=1,Outline=3,Alignment=2,MarginV=60'",
"-t","300",
"-shortest",
"-c:v","libx264",
"-preset","veryfast",
"-crf","23",
"-pix_fmt","yuv420p",
"-movflags","+faststart",
"final_video.mp4"
]

subprocess.run(cmd, check=True)
