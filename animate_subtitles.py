import os
import subprocess

def render_teaching_video():
    print("🎬 EMPIRE PROTOCOL: Starting FFmpeg-Direct Render...")
    
    # 1. Validation
    if not os.path.exists("voice.mp3") or not os.path.exists("subtitles.srt"):
        print("❌ Error: Missing assets.")
        return

    # 2. Get Audio Duration
    cmd_dur = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
    duration = subprocess.check_output(cmd_dur, shell=True).decode().strip()
    
    print(f"🔬 Video Length: {duration} seconds")

    # 3. THE MAGIC COMMAND: 
    # This creates a Navy Blue Background and 'Bakes' the SRT file into the video
    # using the 'subtitles' filter. This avoids all ImageMagick errors.
    
    # Style: Yellow subtitles, Bold, Bottom-Center, with a Shadow
    style = "FontSize=24,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=3,Outline=1,Shadow=1,Alignment=2"
    
    cmd_render = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x0B1D3A:s=1280x720:d={duration}", # Navy Background
        "-i", "voice.mp3", # Audio
        "-vf", f"subtitles=subtitles.srt:force_style='{style}'", # The Professional Subtitles
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", "final_video.mp4"
    ]

    print("🚀 Encoding Masterclass...")
    subprocess.run(cmd_render)
    print("✅ SUCCESS: Professional Video Created.")

if __name__ == "__main__":
    render_teaching_video()
