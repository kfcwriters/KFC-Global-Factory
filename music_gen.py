from manim import *

class NeonLyrics(Scene):
    def construct(self):
        # 1. DARK AESTHETIC BACKGROUND
        # Creating a subtle, dark purple gradient for that late-night vibe
        bg = FullScreenRectangle(fill_opacity=0.2).set_color_gradient([BLACK, "#1a0033"], dict(side=DOWN))
        self.add(bg)

        # 2. THE ROMANTIC LYRICS (Add your Suno AI lyrics here)
        lyric_lines = [
            "In the silence of the night...",
            "Your heartbeat is my only light.",
            "Lost in the melody of us."
        ]

        # 3. ANIMATION LOOP
        for text in lyric_lines:
            # Create the main text
            line = Text(text, font="Georgia", weight=BOLD).scale(0.8)
            
            # Create the "Neon Glow" using a thicker, semi-transparent stroke
            glow = Text(text, font="Georgia", weight=BOLD).scale(0.8)
            glow.set_stroke(color=MAGENTA, width=12, opacity=0.3)
            
            # Group them so they move together
            lyric_group = VGroup(glow, line)
            
            # Animate: Fade in and "Pulse"
            self.play(FadeIn(lyric_group, shift=UP), run_time=1.5)
            self.play(lyric_group.animate.scale(1.1), rate_func=there_and_back, run_time=2)
            self.play(FadeOut(lyric_group, shift=DOWN), run_time=1.5)
            self.wait(0.5)

# To render vertically for Shorts:
# manim -pql --pixel_height 1920 --pixel_width 1080 music_gen.py NeonLyrics
