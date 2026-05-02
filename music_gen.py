from manim import *
import os

class NeonLyrics(Scene):
    def construct(self):
        # 1. TRIPLE CHECK AUDIO
        # This forces Manim to read the audio file before starting
        audio_file = "haryanvi_beat.mp3"
        if os.path.exists(audio_file):
            self.add_sound(audio_file)

        # 2. PREMIUM BACKGROUND
        bg = FullScreenRectangle(fill_opacity=1).set_color("#000000")
        self.add(bg)

        # 3. FONT FIX
        # We use 'Sans' which is the safest global font for Hindi
        text_str = "तेरा यो नशा, मेरी जान ले गया..." 
        
        main_text = Text(text_str, font="Sans", weight=BOLD).scale(0.8).set_color(WHITE)
        glow = Text(text_str, font="Sans", weight=BOLD).scale(0.8)
        glow.set_stroke(color="#D4AF37", width=10, opacity=0.3)
        
        group = VGroup(glow, main_text).center()
        
        # 4. ANIMATION
        self.play(Write(main_text), FadeIn(glow), run_time=3)
        self.play(group.animate.scale(1.1), rate_func=there_and_back, run_time=4)
        self.wait(8) # Ensuring the music plays for the full short
