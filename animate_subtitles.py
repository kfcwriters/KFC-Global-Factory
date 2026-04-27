from manim import *
import os

config.pixel_height = 720
config.pixel_width = 1280
config.frame_rate = 30

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        
        # 1. FIXED HEADER
        title = Text("CLINICAL BIOCHEMISTRY", color=WHITE, weight=BOLD).scale(1.0).to_edge(UP, buff=0.5)
        subtitle = Text("Sigma Metrics & Quality Management", color=YELLOW).scale(0.6).next_to(title, DOWN)
        header_group = VGroup(title, subtitle).fix_in_frame()
        self.add(header_group)

        # 2. THE LONG SCRIPT (Teleprompter Style)
        try:
            with open('lecture_script.txt', 'r') as f:
                full_content = f.read()
        except:
            full_content = "Research assets missing. Please check the Scholar Agent output."

        # We break the text into small paragraphs so it fits the width (Line Wrapping)
        body_text = Paragraph(
            full_content, 
            alignment="center", 
            line_spacing=1.5,
            width=11 # This prevents the 'Cutting' seen in your screenshot
        ).scale(0.6)
        
        # Position text at the bottom to start scrolling up
        body_text.next_to(header_group, DOWN, buff=1).to_edge(DOWN, buff=-10)

        # 3. DURATION CALCULATION
        # A 1500-word script usually takes about 4 minutes (240 seconds)
        # We will scroll the text over the full length of the lecture
        total_time = 240 

        # 4. THE ANIMATION
        self.play(Write(header_group), run_time=2)
        self.wait(1)
        
        # Scrolling effect: Moves the long text from bottom to top
        self.play(
            body_text.animate.shift(UP * 25), # Adjust '25' based on script length
            run_time=total_time,
            rate_func=linear
        )
        
        self.wait(2)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
