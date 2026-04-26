from moviepy.all import ColorClip, TextClip, CompositeVideoClip, AudioFileClip
import pysrt
import os

# Configuration for the "Emperor" Brand
WIDTH, HEIGHT = 1280, 720 
NAVY_BLUE = (11, 29, 58)

def render_kinetic_video():
    print("🎬 DIRECTOR: Generating Motion Subtitles...")
    
    # Check for assets
    if not os.path.exists("voice.mp3") or not os.path.exists("subtitles.srt"):
        print("❌ Error: Missing voice or SRT files.")
        return

    audio = AudioFileClip("voice.mp3")
    bg = ColorClip((WIDTH, HEIGHT), color=NAVY_BLUE, duration=audio.duration)
    
    subs = pysrt.open("subtitles.srt")
    subtitle_clips = []

    for sub in subs:
        start = sub.start.ordinal / 1000
        end = sub.end.ordinal / 1000
        duration = end - start
        
        # Kinetic Typography Engine
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
        
        # Motion Zoom: Prevents the 'frozen screen' perception
        txt = txt.resize(lambda t: 1 + 0.03 * t)
        subtitle_clips.append(txt)

    # Composite and Write
    final = CompositeVideoClip([bg] + subtitle_clips)
    final = final.set_audio(audio)
    
    # Using 'ultrafast' to ensure we stay within GitHub's runtime limits
    final.write_videofile("final_video.mp4", fps=24, codec="libx264", preset="ultrafast")
    print("✅ DIRECTOR: Kinetic Video Completed.")

if __name__ == "__main__":
    render_kinetic_video()
