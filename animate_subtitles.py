import os
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings
import pysrt

change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

def render_viral_video():
    print("🎬 STARTING VIRAL YOUTUBE STYLE RENDER...")
    
    audio = AudioFileClip("voice.mp3")
    max_duration = audio.duration
    bg = ColorClip((1280, 720), color=(11, 29, 58), duration=max_duration)
    
    subs = pysrt.open("subtitles.srt")
    subtitle_clips = []

    for i, sub in enumerate(subs):
        start = sub.start.ordinal / 1000
        if start >= max_duration: continue
        end = min(sub.end.ordinal / 1000, max_duration)
        
        # --- THE 'STARTING' YOUTUBE STYLE (First 5 subtitles) ---
        if i < 5:
            # Big, Bold, Yellow Text for the Hook
            txt = (TextClip(sub.text.upper(),
                    fontsize=75,
                    color='yellow',
                    font='Liberation-Sans-Bold',
                    method='caption',
                    size=(1000, None),
                    stroke_color='black',
                    stroke_width=2) 
                  .set_start(start)
                  .set_duration(end - start)
                  .set_position('center')
                  .set_opacity(1.0))
            
            # Add a 'Pop-in' effect (Grow from 0 to 1)
            txt = txt.resize(lambda t: 0.8 + 0.4*t if t < 0.2 else 1.0)
            
        # --- THE 'TEACHING' STYLE (Remaining subtitles) ---
        else:
            txt = (TextClip(sub.text,
                    fontsize=45,
                    color='white',
                    font='Liberation-Sans-Bold',
                    method='caption',
                    size=(1100, None),
                    bg_color='rgba(0,0,0,0.6)') 
                  .set_start(start)
                  .set_duration(end - start)
                  .set_position(('center', 580)))

        subtitle_clips.append(txt)

    final = CompositeVideoClip([bg] + subtitle_clips).set_audio(audio).set_duration(max_duration)
    final.write_videofile("final_video.mp4", fps=24, codec="libx264", preset="ultrafast")

if __name__ == "__main__":
    render_viral_video()
