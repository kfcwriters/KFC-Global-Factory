import os
import random
import subprocess
from gtts import gTTS

def generate_phd_asset():
    # 1. THE AGENT SCRIPT (The 'ArcReel' Brain)
    topic = "Sigma Metrics & Lab Quality"
    voice_script = f"Welcome to the KFC Lab. In this clinical series, we explore {topic} for institutional excellence."
    
    # 2. GENERATE SPEECH (Totally Free)
    tts = gTTS(text=voice_script, lang='en')
    tts.save("audio.mp3")

    # 3. ARC-REEL STYLE VISUALS (Moving Dashboard + Character Overlay)
    # We use high-contrast graphics that mimic the ArcReel 'Sub-Agent' look
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x000032:s=1280x720:d=30", # Base Layer
        "-i", "audio.mp3", # Audio Layer
        "-vf", (
            "drawgrid=w=64:h=36:t=1:c=white@0.05, " # The 'Data Grid'
            f"drawtext=text='PHD RESEARCH\: {topic}':fontcolor=gold:fontsize=50:x=(w-text_w)/2:y=150, "
            "drawtext=text='VIRTUAL PROFESSOR\: ACTIVE':fontcolor=green:fontsize=20:x=50:y=50, "
            "drawtext=text='KFC LAB ANALYTICS':fontcolor=white:fontsize=30:x=(w-text_w)/2:y=550"
        ),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", "arcreel_style.mp4"
    ]
    subprocess.run(cmd, check=True)
    print("✅ ArcReel-Style Asset Created (Unlimited & Free).")

if __name__ == "__main__":
    generate_phd_asset()
