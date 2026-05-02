from manim import *
import os

class NeonLyrics(Scene):
    def construct(self):
        # 1. Look for the pre-made 15-second track
        if os.path.exists("short_audio.mp3"):
            self.add_sound("short_audio.mp3")

        # 2. Premium Aesthetic (Deep Black & Gold)
        bg = FullScreenRectangle(fill_opacity=1).set_color("#000000")
        self.add(bg)

        # 3. Hindi Text with Proper Font Support
        text_str = "तेरा यो नशा, मेरी जान ले गया..." 
        
        main_text = Text(text_str, font="Sans", weight=BOLD).scale(0.8).set_color(WHITE)
        glow = Text(text_str, font="Sans", weight=BOLD).scale(0.8)
        glow.set_stroke(color="#D4AF37", width=12, opacity=0.3)
        
        group = VGroup(glow, main_text).center()
        
        # 4. Fast, High-Energy Animation for Shorts
        self.play(Write(main_text), FadeIn(glow), run_time=2)
        self.play(group.animate.scale(1.2), rate_func=wiggle, run_time=4)
        self.wait(9) # Total scene duration: 15 seconds
