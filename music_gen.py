from manim import *

class NeonLyrics(Scene):
    def construct(self):
        # Dark aesthetic background
        bg = FullScreenRectangle(fill_opacity=0.1).set_color(BLACK)
        self.add(bg)

        # Romantic Lyric
        text_str = "Lost in the melody of us..."
        
        # Main Text
        line = Text(text_str, font="Georgia", weight=BOLD).scale(0.8)
        # Neon Glow Effect
        glow = Text(text_str, font="Georgia", weight=BOLD).scale(0.8)
        glow.set_stroke(color=MAGENTA, width=10, opacity=0.4)
        
        lyric_group = VGroup(glow, line)
        
        # Animate
        self.play(Write(line), FadeIn(glow), run_time=2)
        self.play(lyric_group.animate.scale(1.1), rate_func=there_and_back, run_time=2)
        self.wait(1)
        self.play(FadeOut(lyric_group))
