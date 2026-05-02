from manim import *

class NeonLyrics(Scene):
    def construct(self):
        # Deep Aesthetic Background
        bg = FullScreenRectangle(fill_opacity=1).set_color("#000000")
        self.add(bg)

        # Haryanvi Lyric
        text_str = "तेरा यो नशा, मेरी जान ले गया..." 
        
        # Gold/White Theme (Matches your PhD project quality)
        main_text = Text(text_str, font="sans-serif", weight=BOLD).scale(0.9).set_color(WHITE)
        glow = Text(text_str, font="sans-serif", weight=BOLD).scale(0.9)
        glow.set_stroke(color="#D4AF37", width=12, opacity=0.3)
        
        group = VGroup(glow, main_text).center()
        
        self.play(Write(main_text), FadeIn(glow), run_time=3)
        self.play(group.animate.scale(1.1), rate_func=there_and_back, run_time=4)
        self.wait(8)
