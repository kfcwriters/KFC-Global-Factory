import subprocess

def render():
    print("🎬 DIRECTOR: Rendering 5-Minute Word-Synced Asset...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=305", # Navy background
        "-i", "voice.mp3",
        "-vf", "drawgrid=w=100:h=100:t=2:c=white@0.1, "
               "subtitles=subtitles.srt:force_style='FontSize=28,Alignment=2,Outline=1'",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-shortest", "final_video.mp4"
    ]
    subprocess.run(cmd)
    print("✅ DIRECTOR: Video Masterpiece Ready.")

if __name__ == "__main__":
    render()
