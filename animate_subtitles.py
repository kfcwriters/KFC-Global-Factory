from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
import pysrt
import os

# Configuration for the "Emperor" Brand
WIDTH, HEIGHT = 1280, 720 # Using 720p for faster GitHub rendering
NAVY_BLUE = (11, 29, 58)

def render_kinetic_video():
    print("🎬 MOTION DIRECTOR: Generating Kinetic Typography...")
    
    audio = AudioFileClip("voice.mp3")
    # Base background layer
    bg = ColorClip((WIDTH, HEIGHT), color=NAVY_BLUE, duration=audio.duration)
    
    subs = pysrt.open("subtitles.srt")
    subtitle_clips = []

    for sub in subs:
        start = sub.start.ordinal / 1000
        end = sub.end.ordinal / 1000
        duration = end - start
        
        # Create animated text block
        txt = (TextClip(sub.text,
                fontsize=60,
                color='white',
                font='Arial-Bold',
                method='caption',
                size=(int(WIDTH*0.8), None))
              .set_start(start)
              .set_duration(duration)
              .set_position(('center', 'center'))
              .fadein(0.2)
              .fadeout(0.2))
        
        # Adding the "Emperor Zoom" - makes the text grow slightly while on screen
        txt = txt.resize(lambda t: 1 + 0.03 * t)
        subtitle_clips.append(txt)

    # Layering: Background + All animated text
    final = CompositeVideoClip([bg] + subtitle_clips)
    final = final.set_audio(audio)

    # Write the file - using 'ultrafast' to prevent GitHub timeout
    final.write_videofile("final_video.mp4", fps=24, codec="libx264", preset="ultrafast")

if __name__ == "__main__":
    render_kinetic_video()
