from manim import *
import os
import subprocess

# MASTER CONFIG: Force Large Display
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
            audio_dur = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            audio_dur = 600

        # 2. LOAD 1200-WORD SCRIPT
        with open('lecture_script.txt', 'r') as f:
            full_content = f.read()

        # 3. FIXED HEADER
        header = Text("PHD CLINICAL BIOCHEMISTRY", color=YELLOW, weight=BOLD).scale(0.6).to_edge(UP, buff=0.2)
        header.fix_in_frame()
        self.add(header)

        # 4. THE BIG FONT FIX (No Empty Screen)
        # Paragraph with a wide width (14) forces Manim to use more horizontal space
        body_text = Paragraph(
            full_content, 
            line_spacing=1.6, 
            alignment="center", 
            width=14 
        )

        # FORCE STRETCH: This pulls the text to the edges, making the font HUGE
        body_text.set_width(config.frame_width - 0.8)
        body_text.next_to(header, DOWN, buff=1)

        # 5. READABLE SCROLL
        scroll_dist = body_text.height + 15
        
        self.play(
            body_text.animate.shift(UP * scroll_dist), 
            run_time=audio_dur, 
            rate_func=linear
        )

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
