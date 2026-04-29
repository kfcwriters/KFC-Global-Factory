from manim import *
import os
import subprocess

# MASTER CONFIG: UPGRADED TO FULL HD
config.pixel_height = 1080 
config.pixel_width = 1920
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

        # 2. LOAD SCRIPT
        with open('lecture_script.txt', 'r') as f:
            words = f.read().split()
        
        # 3. SEGMENTATION: 60 words per slide for MASSIVE visibility
        num_slides = 20
        chunk_size = len(words) // num_slides
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        time_per_slide = total_duration / num_slides

        for i, chunk in enumerate(chunks):
            # HEADER - Increased scale for 1080p
            header = Text(f"PHD MASTERCLASS | PART {i+1}", color=YELLOW, weight=BOLD).scale(1.2).to_edge(UP, buff=0.5)
            
            # THE FONT FIX:
            # - width=16: At 1080p, this forces the text to the very edges.
            # - scale(1.8): This makes the letters physically massive.
            body = Paragraph(
                chunk, 
                line_spacing=1.5, 
                alignment="center", 
                width=16, 
                color=WHITE
            ).scale(1.8) 
            
            body.next_to(header, DOWN, buff=1)

            # STATIC RENDER: Instant speed, no loops
            self.add(header, body)
            self.wait(time_per_slide)
            self.remove(header, body)

if __name__ == "__main__":
    # We use -qh (High Quality) to match the 1080p config
    os.system("manim -qh animate_subtitles.py TeachingMasterclass --media_dir ./media")
