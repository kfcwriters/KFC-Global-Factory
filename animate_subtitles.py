import os
import PIL.Image

# --- THE PILLOW PATCH (CRITICAL FIX) ---
# This fixes the 'AttributeError: module PIL.Image has no attribute ANTIALIAS'
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# ---------------------------------------

from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
import pysrt

# Video Specifications
WIDTH, HEIGHT = 1280, 720 
NAVY_BLUE = (11, 29, 58) # Institutional Deep Blue

def render_kinetic_video():
    print("🎬 DIRECTOR: Initializing Kinetic Typography Engine...")
    
    # Validation
    if not os.path.exists("voice.mp3") or not os.path.exists("subtitles.srt"):
        print("❌ Error: Assets missing. Ensure Agent 03 finished correctly.")
        return

    # Load Assets
    audio = AudioFileClip("voice.mp3")
    background = ColorClip((WIDTH, HEIGHT), color=NAVY_BLUE, duration=audio.duration)
    
    subs = pysrt.open("subtitles.srt")
    subtitle_clips = []

    print(f"🔬 DIRECTOR: Processing {len(subs)} subtitle segments...")

    for sub in subs:
        start = sub.start.ordinal / 1000
        end = sub.end.ordinal / 1000
        duration = end - start
        
        # Create Text Layer
        txt = (TextClip(sub.text,
                fontsize=55,
                color='white',
                font='Liberation-Sans-Bold', # Standard Linux font
                method='caption',
                size=(int(WIDTH*0.8), None))
              .set_start(start)
              .set_duration(duration)
              .set_position(('center', 'center'))
              .fadein(0.2)
              .fadeout(0.2))
        
        # KINETIC ANIMATION: Subtle 2% zoom over time to keep the eye engaged
        txt = txt.resize(lambda t: 1 + 0.02 * t)
        
        subtitle_clips.append(txt)

    # Composite Layers: Background + All moving text clips
    final_composition = CompositeVideoClip([background] + subtitle_clips)
    final_composition = final_composition.set_audio(audio)

    # Export Video
    print("🎬 DIRECTOR: Encoding final master (ultrafast)...")
    final_composition.write_videofile(
        "final_video.mp4", 
        fps=24, 
        codec="libx264", 
        preset="ultrafast",
        audio_codec="aac"
    )
    print("✅ DIRECTOR: Asset 'final_video.mp4' is ready for Courier.")

if __name__ == "__main__":
    render_kinetic_video()
