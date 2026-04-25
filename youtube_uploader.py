import os
import subprocess

def create_720p_video():
    print("🎬 FFmpeg Engine: Generating 720p Clinical Asset...")
    
    # Text for the clinical asset
    text = "HbA1c: Gold Standard Monitoring\nLaboratory Quality Management"
    
    # Command to create a 5-second 720p blue video with white text
    cmd = (
        f'ffmpeg -y -f lavfi -i color=c=0x000032:s=1280x720:d=5 '
        f'-vf "drawtext=text=\'{text}\':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=(h-text_h)/2" '
        f'-c:v libx264 -pix_fmt yuv420p clinical_asset_720p.mp4'
    )
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("✅ Asset Rendered: clinical_asset_720p.mp4")
    except Exception as e:
        print(f"❌ FFmpeg Error: {e}")

if __name__ == "__main__":
    create_720p_video()
