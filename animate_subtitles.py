from manim import *
import os

# TURBO CONFIG: Lower resolution for ultra-fast processing
config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15 # Lower frame rate for teaching videos saves 50% time

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        
        # 1. FIXED HEADER
        title = Text("CLINICAL BIOCHEMISTRY", color=WHITE, weight=BOLD).scale(0.8)
        subtitle = Text("Sigma Metrics & Quality Management", color=YELLOW).scale(0.5)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.3)
        self.add(header)

        # 2. THE TEXT BLOCK (Non-Animated for Speed)
        try:
            with open('lecture_script.txt', 'r') as f:
                full_content = f.read()
        except:
            full_content = "Laboratory assets missing. Initializing backup protocol."

        # We use Text() instead of Paragraph() for high-speed block rendering
        body_text = Text(
            full_content, 
            line_spacing=1.2,
            t2c={'Sigma': RED, 'Quality': YELLOW}, # Highlight key words
            font_size=20
        ).scale(0.8)
        
        body_text.next_to(header, DOWN, buff=1)

        # 3. THE SCROLL (Linear and Fast)
        # We scroll the whole block at once instead of letter-by-letter
        total_time = 240 # 4 Minutes
        
        self.play(
            body_text.animate.shift(UP * (body_text.height + 5)), 
            run_time=total_time,
            rate_func=linear
        )

if __name__ == "__main__":
    # Internal command to render in 'Low Quality' for speed
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
