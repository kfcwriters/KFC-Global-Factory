import os
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings
import pysrt

change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def render():
    print("🎬 STARTING RENDER WITH DURATION GUARD...")
    
    audio = AudioFileClip("voice.mp3")
    max_duration = audio.duration # This is our 'hard limit'
    
    bg = ColorClip((1280, 720), color=(11, 29, 58), duration=max_duration)
    
    subs = pysrt.open("subtitles.srt")
    subtitle_clips = []

    for sub in subs:
        start = sub.start.ordinal / 1000
        # GUARD: If the subtitle starts after the audio ends, skip it
        if start >= max_duration:
            continue
            
        # GUARD: Ensure the subtitle end doesn't exceed the audio length
        end = min(sub.end.ordinal / 1000, max_duration)
        duration = end - start
        
        if duration <= 0:
            continue

        txt = (TextClip(sub.text,
                fontsize=40,
                color='white',
                font='Liberation-Sans-Bold',
                method='caption',
                size=(1100, None),
                bg_color='rgba(0,0,0,0.6)') 
              .set_start(start)
              .set_duration(duration)
              .set_position(('center', 550)))
        
        subtitle_clips.append(txt)

    # Composite only up to the exact audio duration
    final = CompositeVideoClip([bg] + subtitle_clips).set_audio(audio).set_duration(max_duration)
    
    print(f"🎬 Rendering {max_duration} seconds of video...")
    final.write_videofile("final_video.mp4", fps=20, codec="libx264", preset="ultrafast")

if __name__ == "__main__":
    render()
