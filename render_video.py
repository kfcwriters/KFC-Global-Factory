import subprocess

def render():
    print("🎬 DIRECTOR: Forcing Subtitle Burn...")
    
    # 1. We create a dedicated subtitle file that matches the 5-minute length
    with open("master.srt", "w") as f:
        for i in range(1, 40): # 40 blocks of 8 seconds each
            start = (i-1) * 8
            end = i * 8
            f.write(f"{i}\n00:00:{start:02},000 --> 00:00:{end:02},000\n")
            f.write("ADVANCED SIGMA METRIC ANALYSIS: PHD MASTERCLASS\n\n")

    # 2. Hard-burn the subtitles with a high-visibility background
    # This physically writes the text into the pixels of the video
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=305", 
        "-i", "voice.mp3",
        "-vf", "drawgrid=w=100:h=100:t=2:c=white@0.1, "
               "subtitles=master.srt:force_style='Alignment=2,FontSize=28,PrimaryColour=&H00FFFF,Outline=1'",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-shortest", "final_video.mp4"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ DIRECTOR: Hard-Burned Masterpiece Ready.")
    except Exception as e:
        print(f"❌ DIRECTOR FAILED: {e}")

if __name__ == "__main__":
    render()
