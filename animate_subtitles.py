import os
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings
import pysrt

# Force Path
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def render():
    print("🎬 STARTING 3-MINUTE TEACHING RENDER...")
    
    audio = AudioFileClip("voice.mp3").subclip(0, 210) # Cap at 3.5 minutes
    bg = ColorClip((1280, 720), color=(11, 29, 58), duration=audio.duration)
    
    subs = pysrt.open("subtitles.srt")
    subtitle_clips = []

    for sub in subs:
        start = sub.start.ordinal / 1000
        if start >= audio.duration: break
        end = min(sub.end.ordinal / 1000, audio.duration)
        
        # TEACHING STYLE: White text on a semi-transparent black bar
        txt = (TextClip(sub.text,
                fontsize=40,
                color='white',
                font='Liberation-Sans-Bold',
                method='caption',
                size=(1100, None),
                bg_color='rgba(0,0,0,0.6)') 
              .set_start(start)
              .set_duration(end - start)
              .set_position(('center', 550))) # Bottom-center
        
        subtitle_clips.append(txt)

    final = CompositeVideoClip([bg] + subtitle_clips).set_audio(audio)
    final.write_videofile("final_video.mp4", fps=20, codec="libx264", preset="ultrafast")

if __name__ == "__main__":
    render()
