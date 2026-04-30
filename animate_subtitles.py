from manim import *
import os
import textwrap

# MASTER CONFIG: 720p (Perfect Balance)
config.pixel_height = 720 
config.pixel_width = 1280
config.frame_rate = 15
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Navy
        
        # 1. ASSET VALIDATION
        if not os.path.exists('lecture_script.txt'):
            print("ERROR: Script missing!")
            return

        # 2. LOAD SCRIPT
        with open('lecture_script.txt', 'r') as f:
            script_text = f.read()
        
        # 3. SEGMENTATION: 30 words per slide for GIANT FONT
        words = script_text.split()
        chunk_size = 30 
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        
        # 12 minutes total
        time_per_slide = 720 / len(chunks)

        for i, chunk in enumerate(chunks):
            # HEADER
            header = Text(f"PHD MASTERCLASS | PART {i+1}", color=YELLOW, weight=BOLD).scale(0.8).to_edge(UP, buff=0.4)
            
            # THE FONT FIX:
            # - Wrap width 35 forces the text to fill the center
            # - font_size 42 makes it huge on mobile
            wrapped_text = "\n".join(textwrap.wrap(chunk, width=35))
            body = Text(
                wrapped_text, 
                font_size=42, 
                line_spacing=1.5, 
                color=WHITE,
                alignment=CENTER
            )
            
            body.next_to(header, DOWN, buff=0.6)

            # RENDER: Static page-turn
            self.add(header, body)
            self.wait(time_per_slide)
            self.remove(header, body)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
