from manim import *
import os
import subprocess
import textwrap

# MASTER CONFIG: 720p for Stability
config.pixel_height = 720 
config.pixel_width = 1280
config.frame_rate = 15
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Navy
        
        # 1. AUDIO SYNC
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            total_duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            total_duration = 600

        # 2. LOAD SCRIPT
        with open('lecture_script.txt', 'r') as f:
            script_text = f.read()
        
        # 3. SEGMENTATION: 35 words per slide = MASSIVE Font
        words = script_text.split()
        chunk_size = 35 
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        time_per_slide = total_duration / len(chunks)

        for i, chunk in enumerate(chunks):
            # HEADER
            header = Text(f"PHD MASTERCLASS | PART {i+1}", color=YELLOW, weight=BOLD).scale(0.8).to_edge(UP, buff=0.4)
            
            # THE FONT FIX:
            # - We wrap at 35 chars to use the whole screen width
            # - font_size 40 is physically massive on 720p
            wrapped_text = "\n".join(textwrap.wrap(chunk, width=35))
            body = Text(
                wrapped_text, 
                font_size=40, 
                line_spacing=1.5, 
                color=WHITE,
                alignment=CENTER
            )
            
            body.next_to(header, DOWN, buff=0.6)

            # RENDER: Page-turn method (Fast & Stable)
            self.add(header, body)
            self.wait(time_per_slide)
            self.remove(header, body)

if __name__ == "__main__":
    # We use -ql for speed and to prevent runner timeouts
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
