from manim import *
import os
import subprocess
import textwrap

# MASTER CONFIG: FULL HD 1080p
config.pixel_height = 1080 
config.pixel_width = 1920
config.frame_rate = 15
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            total_duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            total_duration = 720 

        with open('lecture_script.txt', 'r') as f:
            script_text = f.read()
        
        words = script_text.split()
        # 40 words per slide for MASSIVE visibility
        chunk_size = 40 
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        time_per_slide = total_duration / len(chunks)

        for i, chunk in enumerate(chunks):
            header = Text(f"PHD MASTERCLASS | PART {i+1}", color=YELLOW, weight=BOLD).scale(1.2).to_edge(UP, buff=0.5)
            
            # GOLDEN RATIO FONT: 
            # - Wrap width 40 avoids the edges
            # - font_size 48 is huge but fits the 1080p frame
            wrapped_text = "\n".join(textwrap.wrap(chunk, width=40))
            body = Text(wrapped_text, font_size=48, line_spacing=1.5, color=WHITE, alignment=CENTER)
            body.next_to(header, DOWN, buff=0.8)

            self.add(header, body)
            self.wait(time_per_slide)
            self.remove(header, body)

if __name__ == "__main__":
    # Lower quality flag (-ql) to save memory during the 1200-word render
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
