from manim import *

class VisualLyrics(Scene):
    def construct(self):
        # 1. Solid Professional Background 
        # (Using pure black for that premium lyrics video look)
        bg = FullScreenRectangle(fill_opacity=1).set_color("#000000")
        self.add(bg)

        # 2. The Text Content
        text_str = "तेरा यो नशा, मेरी जान ले गया..." 
        
        # 3. Create the Main Text & Glow
        # We use 'Sans' as it's the most stable font for Hindi on Linux
        main_text = Text(text_str, font="Sans", weight=BOLD).scale(0.8)
        main_text.set_color(WHITE)
        
        # Gold Glow effect
        glow = Text(text_str, font="Sans", weight=BOLD).scale(0.8)
        glow.set_stroke(color="#D4AF37", width=12, opacity=0.3)
        
        # Group them to animate together
        group = VGroup(glow, main_text).center()
        
        # 4. Smooth Professional Animation Sequence
        # This timing (3s + 5s + 7s) adds up to exactly 15 seconds
        self.play(Write(main_text), FadeIn(glow), run_time=3)
        self.play(group.animate.scale(1.15), rate_func=there_and_back, run_time=5)
        
        # Wait for the remaining time to keep the text on screen for the song
        self.wait(7)
