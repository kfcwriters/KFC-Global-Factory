from manim import *
import os

config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15
config.verbosity = "ERROR"

class TeachingLoop(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Institutional Navy
        
        # 1. Branding Header
        title = Text("PHD RESEARCH MASTERCLASS", weight=BOLD, color=WHITE).scale(0.8).to_edge(UP)
        subtitle = Text("Clinical Biochemistry & Lab Management", color=YELLOW).scale(0.5).next_to(title, DOWN)
        
        # 2. Visual Frame
        frame = RoundedRectangle(corner_radius=0.2, height=4.5, width=7.5, color=BLUE_B)
        status = Text("• LECTURE IN PROGRESS", color=GREEN, font_size=18).next_to(frame, UP, buff=0.1)
        
        self.add(title, subtitle, frame, status)
        
        # 3. Micro-Animation (Very fast to render)
        self.play(status.animate.set_opacity(0.3), run_time=1)
        self.play(status.animate.set_opacity(1), run_time=1)
        self.wait(1)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingLoop --media_dir ./media")
