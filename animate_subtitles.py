import PIL.Image
# PILLOW COMPATIBILITY PATCH
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
import pysrt
import os

WIDTH, HEIGHT = 1280, 720 
NAVY_BLUE = (11, 29, 58)

def render():
    print("🎬 DIRECTOR: Starting Kinetic Render...")
    
    if not os.path.exists("voice.mp3") or not os.path.exists("subtitles.srt"):
        print("❌ Error: Missing assets.")
        return

    audio = AudioFileClip("voice.mp3")
    bg = ColorClip((WIDTH, HEIGHT), color=NAVY_BLUE, duration=audio.duration)
    
    subs = pysrt.open("subtitles.srt")
    subtitle_clips = []

    for sub in subs:
        start = sub.start.ordinal / 1000
        end = sub.end.ordinal / 1000
        
        txt = (TextClip(sub.text,
                fontsize=55,
                color='white',
                font='Liberation-Sans-Bold',
                method='caption',
                size=(int(WIDTH*0.8), None))
              .set_start(start)
              .set_duration(end - start)
              .set_position(('center', 'center'))
              .fadein(0.2)
              .fadeout(0.2))
        
        # Kinetic Zoom for "Non-Frozen" Perception
        txt = txt.resize(lambda t: 1 + 0.02 * t)
        subtitle_clips.append(txt)

    final = CompositeVideoClip([bg] + subtitle_clips)
    final = final.set_audio(audio)
    final.write_videofile("final_video.mp4", fps=24, codec="libx264", preset="ultrafast")
    print("✅ DIRECTOR: Kinetic Video Ready.")

if __name__ == "__main__":
    render()
