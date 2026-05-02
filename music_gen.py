from manim import *
import os

class NeonLyrics(Scene):
    def construct(self):
        # 1. Add Sound (Automatically clipped to video length)
        if os.path.exists("background_music.mp3"):
            self.add_sound("background_music.mp3")

        # 2. Add Romantic Background Image
        # I am adding a rectangle with a gradient to look "Romantic" 
        # since we don't have an image file yet.
        bg = Rectangle(
            width=config.frame_width, 
            height=config.frame_height,
            fill_color=[PINK, DARK_BROWN], # Romantic gradient
            fill_opacity=0.5,
            stroke_width=0
        )
        self.add(bg)

        # 3. Haryanvi / Hindi Lyric
        text_str = "तेरा यो नशा, मेरी जान ले गया..." 
        
        line = Text(text_str, font="sans-serif", weight=BOLD).scale(0.8)
        glow = Text(text_str, font="sans-serif", weight=BOLD).scale(0.8)
        glow.set_stroke(color=WHITE, width=15, opacity=0.3) # White glow for romance
        
        lyric_group = VGroup(glow, line).center()
        
        # 4. Animation
        self.play(FadeIn(bg), run_time=2)
        self.play(Write(line), FadeIn(glow), run_time=3)
        self.play(lyric_group.animate.scale(1.1).set_color(YELLOW), rate_func=there_and_back, run_time=5)
        self.wait(5) # Keeps the romantic vibe on screen
