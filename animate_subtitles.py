from manim import *
import os
import subprocess
import textwrap

# MASTER CONFIG: FULL HD
config.pixel_height = 1080 
config.pixel_width = 1920
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
            total_duration = 720 # 12 mins fallback

        # 2. LOAD SCRIPT
        with open('lecture_script.txt', 'r') as f:
            script_text = f.read()
        
        # 3. SEGMENTATION: 50 words per slide for MASSIVE visibility
        words = script_text.split()
        chunk_size = 50 
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        time_per_slide = total_duration / len(chunks)

        for i, chunk in enumerate(chunks):
            # HEADER - Professional & Large
            header = Text(f"PHD MASTERCLASS | PART {i+1}", color=YELLOW, weight=BOLD).scale(1.5).to_edge(UP, buff=0.7)
            
            # THE FONT FIX:
            # - We wrap the text at 45 characters per line
            # - We set a fixed font_size=55 (Huge for 1080p)
            wrapped_text = "\n".join(textwrap.wrap(chunk, width=45))
            body = Text(
                wrapped_text, 
                font_size=55, 
                line_spacing=1.8, 
                color=WHITE,
                t2c={chunk: WHITE} # Ensures high contrast
            )
            
            body.next_to(header, DOWN, buff=1)

            # RENDER: Static page-turn for speed and clarity
            self.add(header, body)
            self.wait(time_per_slide)
            self.remove(header, body)

if __name__ == "__main__":
    # We use -qh to ensure the 1080p resolution is applied
    os.system("manim -qh animate_subtitles.py TeachingMasterclass --media_dir ./media")
