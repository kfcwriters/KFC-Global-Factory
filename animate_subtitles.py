from manim import *
import os
import subprocess
import textwrap

# MASTER CONFIG: 720p (Perfect for Large Fonts & Stability)
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
            total_duration = 720 

        # 2. LOAD SCRIPT
        if os.path.exists('lecture_script.txt'):
            with open('lecture_script.txt', 'r') as f:
                script_text = f.read()
        else:
            script_text = "Data Sync Error."
        
        # 3. SEGMENTATION: 30 words per slide = MASSIVE Font
        words = script_text.split()
        chunk_size = 30 
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        time_per_slide = total_duration / len(chunks)

        for i, chunk in enumerate(chunks):
            # HEADER
            header = Text(f"PHD MASTERCLASS | PART {i+1}", color=YELLOW, weight=BOLD).scale(0.8).to_edge(UP, buff=0.4)
            
            # THE FONT FIX:
            # - Wrap width 35 keeps text centered and huge
            # - font_size 42 on 720p looks like a giant headline
            wrapped_text = "\n".join(textwrap.wrap(chunk, width=35))
            body = Text(
                wrapped_text, 
                font_size=42, 
                line_spacing=1.4, 
                color=WHITE,
                alignment=CENTER
            )
            
            body.next_to(header, DOWN, buff=0.6)

            # RENDER
            self.add(header, body)
            self.wait(time_per_slide)
            self.remove(header, body)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
