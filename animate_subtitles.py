from manim import *
import os
import subprocess

config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        
        # 1. Sync Logic
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            total_duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            total_duration = 600

        # 2. Load and Split Script
        with open('lecture_script.txt', 'r') as f:
            words = f.read().split()
        
        # Split into 10 smaller "Slides" for perfect readability
        num_slides = 10
        chunk_size = len(words) // num_slides
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        time_per_slide = total_duration / num_slides

        for i, chunk in enumerate(chunks):
            # FIXED HEADER
            header = Text(f"PHD LECTURE: PART {i+1}", color=YELLOW, weight=BOLD).scale(0.6).to_edge(UP, buff=0.3)
            
            # SLIDE CONTENT - We use a simple Paragraph with NO animation to stop the loop
            body = Paragraph(chunk, line_spacing=1.5, alignment="center", width=11).scale(0.6)
            body.next_to(header, DOWN, buff=0.5)

            # RENDER: Just a simple FadeIn/FadeOut. 
            # This is 100x faster than 'Scrolling' or 'Writing'
            self.add(header, body)
            self.wait(time_per_slide)
            self.remove(header, body)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
