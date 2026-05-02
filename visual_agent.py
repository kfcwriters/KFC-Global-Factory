from manim import *

class VisualLyrics(Scene):
    def construct(self):
        # Deep Black Background
        self.add(FullScreenRectangle(fill_opacity=1).set_color("#000000"))

        text_str = "तेरा यो नशा, मेरी जान ले गया..." 
        
        # Professional Gold/White Look
        main_text = Text(text_str, font="Sans", weight=BOLD).scale(0.8).set_color(WHITE)
        glow = Text(text_str, font="Sans", weight=BOLD).scale(0.8)
        glow.set_stroke(color="#D4AF37", width=12, opacity=0.3)
        
        group = VGroup(glow, main_text).center()
        
        self.play(Write(main_text), FadeIn(glow), run_time=3)
        self.play(group.animate.scale(1.1), rate_func=there_and_back, run_time=5)
        self.wait(7) # Total 15 Seconds
