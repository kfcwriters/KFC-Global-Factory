from manim import *
import os

class NeonLyrics(Scene):
    def construct(self):
        # Add the audio file
        if os.path.exists("background_music.mp3"):
            self.add_sound("background_music.mp3")

        # Dark aesthetic background
        bg = FullScreenRectangle(fill_opacity=0.3).set_color(BLACK)
        self.add(bg)

        # Haryanvi / Hindi Romantic Lyric
        text_str = "तेरा यो नशा..." 
        
        # Create the text layers
        line = Text(text_str, font="sans-serif", weight=BOLD).scale(0.9)
        glow = Text(text_str, font="sans-serif", weight=BOLD).scale(0.9)
        
        # Neon Pink Glow effect
        glow.set_stroke(color="#FF00FF", width=12, opacity=0.4)
        
        lyric_group = VGroup(glow, line)
        
        # Animation sequence (Total 10-12 seconds)
        self.play(Write(line), FadeIn(glow), run_time=3)
        self.play(lyric_group.animate.scale(1.2), rate_func=there_and_back, run_time=4)
        self.wait(3) # Wait while music plays
        self.play(FadeOut(lyric_group), run_time=2)
