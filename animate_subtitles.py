from manim import *
import os

# TURBO SETTINGS
config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15 
config.verbosity = "ERROR" # Stops the massive logs seen in image_5bb692.jpg

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        
        # 1. FIXED HEADER
        title = Text("CLINICAL BIOCHEMISTRY", color=WHITE, weight=BOLD).scale(0.8)
        subtitle = Text("Sigma Metrics & Quality Management", color=YELLOW).scale(0.5)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.3)
        self.add(header)

        # 2. THE TEXT BLOCK
        try:
            with open('lecture_script.txt', 'r') as f:
                full_content = f.read()
        except:
            full_content = "Assets missing. Re-initializing factory protocol..."

        # Using Text() with 'disable_ligatures' makes rendering 5x faster
        body_text = Text(
            full_content, 
            line_spacing=1.5,
            font_size=24,
            disable_ligatures=True 
        ).scale(0.6)
        
        body_text.next_to(header, DOWN, buff=1)

        # 3. THE SCROLL
        total_time = 240 # 4 Minutes
        
        # We use a simple 'shift' which doesn't require calculating sub-objects
        self.play(
            body_text.animate.shift(UP * (body_text.height + 10)), 
            run_time=total_time,
            rate_func=linear
        )

if __name__ == "__main__":
    # Internal command for 'Low Quality' speed
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
