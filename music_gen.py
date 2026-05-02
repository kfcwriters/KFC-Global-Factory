from manim import *

class NeonLyrics(Scene):
    def construct(self):
        # 1. Load the Audio (Hindi/Haryanvi track)
        self.add_sound("background_music.mp3")

        # Background aesthetic
        bg = FullScreenRectangle(fill_opacity=0.2).set_color(BLACK)
        self.add(bg)

        # Romantic Lyric
        text_str = "तू चीज़ लाजवाब, तेरा कोई ना जवाब..." # Example Haryanvi Lyric
        
        # Main Text & Neon Glow
        line = Text(text_str, font="sans-serif", weight=BOLD).scale(0.7)
        glow = Text(text_str, font="sans-serif", weight=BOLD).scale(0.7)
        glow.set_stroke(color="#FF00FF", width=12, opacity=0.3)
        
        lyric_group = VGroup(glow, line)
        
        # Animation timed to the music
        self.play(Write(line), FadeIn(glow), run_time=3)
        self.play(lyric_group.animate.scale(1.2), rate_func=there_and_back, run_time=2)
        self.wait(5) # Keeps the music playing for 5 more seconds
        self.play(FadeOut(lyric_group))
