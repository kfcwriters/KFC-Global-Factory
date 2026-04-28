from manim import *
import os

# HARD CONFIG: Optimized for fast rendering on GitHub
config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15 
config.format = "mp4"
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Institutional Navy
        
        # 1. FIXED HEADER
        title = Text("CLINICAL BIOCHEMISTRY", color=WHITE, weight=BOLD).scale(0.8)
        subtitle = Text("Sigma Metrics & Quality Management", color=YELLOW).scale(0.5)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.3)
        self.add(header)

        # 2. LOAD SCRIPT
        try:
            with open('lecture_script.txt', 'r') as f:
                full_content = f.read()
        except:
            full_content = "PhD Lecture Assets Generating..."

        # 3. TELEPROMPTER BODY
        # We use Text for speed and set a width so it doesn't bleed off screen
        body_text = Text(full_content, font_size=22, line_spacing=1.5).scale(0.7)
        body_text.next_to(header, DOWN, buff=1)

        # 4. THE 4-MINUTE SCROLL (240 Seconds)
        self.play(
            body_text.animate.shift(UP * (body_text.height + 10)), 
            run_time=240, 
            rate_func=linear
        )

if __name__ == "__main__":
    # Internal command to ensure files go to the right folder
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
