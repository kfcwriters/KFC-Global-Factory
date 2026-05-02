from manim import *
import os

class NeonLyrics(Scene):
    def construct(self):
        if os.path.exists("background_music.mp3"):
            self.add_sound("background_music.mp3")

        # Premium Deep Background
        bg = FullScreenRectangle(fill_opacity=1).set_color("#0F0F0F")
        self.add(bg)

        # Haryanvi Lyric - Using a "Gold & White" Professional Theme
        text_str = "तेरा यो नशा, मेरी जान ले गया..." 
        
        # Main Text (White)
        line = Text(text_str, font="sans-serif", weight=BOLD).scale(0.8)
        # Subtle Gold Glow (Not irritating fake colors)
        glow = Text(text_str, font="sans-serif", weight=BOLD).scale(0.8)
        glow.set_stroke(color="#D4AF37", width=8, opacity=0.3) 
        
        lyric_group = VGroup(glow, line).center()
        
        # Smooth Professional Animation
        self.play(FadeIn(bg), run_time=1)
        self.play(Write(line), FadeIn(glow), run_time=2)
        # Gentle "Pulse" animation to match the beat
        self.play(lyric_group.animate.scale(1.1), rate_func=slow_into_fast, run_time=3)
        self.wait(7)
        self.play(FadeOut(lyric_group), run_time=2)
