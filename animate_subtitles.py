import os
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings
import pysrt

# Mandatory Binary Path for GitHub Runners
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def render_teaching_video():
    print("🎓 PROFESSOR AGENT: Rendering Educational Masterclass...")
    
    if not os.path.exists("voice.mp3"):
        print("❌ Error: Voice file missing.")
        return

    audio = AudioFileClip("voice.mp3")
    # Using 'Institutional Navy' for the background
    bg = ColorClip((1280, 720), color=(11, 29, 58), duration=audio.duration)
    
    subs = pysrt.open("subtitles.srt")
    subtitle_clips = []

    for sub in subs:
        start = sub.start.ordinal / 1000
        end = sub.end.ordinal / 1000
        
        # --- THE TEACHING STYLE UI ---
        # We add a 'bg_color' to create a high-contrast box around the text
        txt = (TextClip(sub.text,
                fontsize=45,
                color='white',
                font='Liberation-Sans-Bold',
                method='caption',
                size=(1000, None),
                align='center',
                bg_color='rgba(0,0,0,0.5)') # 50% transparent black box
              .set_start(start)
              .set_duration(end - start)
              .set_position(('center', 600)) # Positioned at the bottom third
              .fadein(0.15))
        
        # ADDING MOTION: A subtle zoom makes the 'teaching' feel active
        txt = txt.resize(lambda t: 1 + 0.01*t)
        
        subtitle_clips.append(txt)

    # Adding a 'Title Card' at the start for professionalism
    title = (TextClip("CLINICAL BIOCHEMISTRY:\nSIGMA METRICS MASTERCLASS", 
             fontsize=70, color='yellow', font='Liberation-Sans-Bold')
             .set_duration(4)
             .set_position('center')
             .fadeout(1))

    final = CompositeVideoClip([bg, title] + subtitle_clips)
    final = final.set_audio(audio)
    
    final.write_videofile("final_video.mp4", fps=24, codec="libx264", preset="ultrafast")
    print("✅ SUCCESS: Teaching video with high-contrast subtitles ready.")

if __name__ == "__main__":
    render_teaching_video()
