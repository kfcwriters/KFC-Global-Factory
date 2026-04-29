from manim import *
import os
import subprocess

# MASTER CONFIG: Ultra-Wide for Big Font
config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Institutional Navy
        
        # 1. AUDIO SYNC
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            total_duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            total_duration = 600

        with open('lecture_script.txt', 'r') as f:
            full_content = f.read()

        # 2. FIXED HEADER
        header = Text("PHD CLINICAL BIOCHEMISTRY", color=YELLOW, weight=BOLD).scale(0.6).to_edge(UP, buff=0.2)
        header.fix_in_frame()
        self.add(header)

        # 3. THE "SCREEN-FILLER" FONT FIX
        # width=14 forces the internal engine to think the screen is giant
        body_text = Paragraph(
            full_content, 
            line_spacing=1.5, 
            alignment="center", 
            width=14 
        )

        # THIS IS THE KEY: We stretch the text block to 95% of the screen width.
        # This physically pulls the letters apart and makes them HUGE.
        body_text.set_width(config.frame_width - 0.6)
        body_text.next_to(header, DOWN, buff=1)

        # 4. THE READABLE SCROLL
        scroll_distance = body_text.height + 10
        
        self.play(
            body_text.animate.shift(UP * scroll_distance), 
            run_time=total_duration, 
            rate_func=linear
        )

if __name__ == "__main__":
    # We use explicit naming to ensure the YML can find the file
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
