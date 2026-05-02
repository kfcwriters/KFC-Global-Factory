from manim import *
import os

class NeonLyrics(Scene):
    # Set the 720p vertical config inside the script for safety
    config.pixel_height = 1280
    config.pixel_width = 720
    config.frame_rate = 30

    def construct(self):
        if os.path.exists("background_music.mp3"):
            self.add_sound("background_music.mp3")

        bg = FullScreenRectangle(fill_opacity=0.15).set_color(BLACK)
        self.add(bg)

        # Haryanvi Lyric - Scaled for 720p
        text_str = "तेरा यो नशा, मेरी जान ले गया..." 
        
        line = Text(text_str, font="sans-serif", weight=BOLD).scale(0.6) # Reduced scale for 720p
        glow = Text(text_str, font="sans-serif", weight=BOLD).scale(0.6)
        glow.set_stroke(color="#FF00FF", width=10, opacity=0.3) # Slightly thinner glow for lower res
        
        lyric_group = VGroup(glow, line)
        
        self.play(Write(line), FadeIn(glow), run_time=2)
        self.play(lyric_group.animate.scale(1.1), rate_func=there_and_back, run_time=3)
        self.wait(4)
        self.play(FadeOut(lyric_group))
