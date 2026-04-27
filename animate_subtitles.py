from manim import *
import os

# Global configuration for speed and stability
config.pixel_height = 720
config.pixel_width = 1280
config.frame_rate = 30

class TeachingMasterclass(Scene):
    def construct(self):
        # 1. Background Setup
        self.camera.background_color = "#0B1D3A"
        
        # 2. FIXED HEADER (Removed the 'fix_in_frame' error)
        title = Text("CLINICAL BIOCHEMISTRY", color=WHITE, weight=BOLD).scale(0.9)
        subtitle = Text("Sigma Metrics & Quality Management", color=YELLOW).scale(0.6)
        header_group = VGroup(title, subtitle).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.5)
        
        # We add the header to the scene immediately
        self.add(header_group)

        # 3. LOADING THE LONG SCRIPT
        try:
            with open('lecture_script.txt', 'r') as f:
                full_content = f.read()
        except:
            full_content = "Academic assets missing. Initializing laboratory protocol simulation..."

        # 4. TELEPROMPTER BODY
        # 'line_spacing' and 'width' ensure it fits within the screen borders
        body_text = Paragraph(
            full_content, 
            alignment="center", 
            line_spacing=1.5,
            width=11 
        ).scale(0.6)
        
        # Position starting point just below the header
        body_text.next_to(header_group, DOWN, buff=1)

        # 5. DURATION CALCULATION
        # Match this to your actual audio length (e.g., 240 seconds for 4 minutes)
        total_time = 240 

        # 6. THE ANIMATION
        self.play(Write(header_group), run_time=2)
        self.wait(1)
        
        # Smooth Scroll: Moves the text from bottom to top
        # We move it UP by a factor of its own height to ensure every line is seen
        self.play(
            body_text.animate.shift(UP * (body_text.height + 2)), 
            run_time=total_time,
            rate_func=linear
        )
        
        self.wait(2)

if __name__ == "__main__":
    # Internal render command
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
