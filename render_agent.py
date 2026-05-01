from manim import *
import os

config.pixel_height, config.pixel_width = 720, 1280
config.frame_rate = 15
config.verbosity = "ERROR"

class PhDArchitect(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        
        with open('lecture_script.txt', 'r') as f:
            content = f.read()

        # SEGMENTATION: 25 words per slide for MAXIMUM FONT SIZE
        words = content.split()
        chunk_size = 25
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        
        # Audio Duration Sync (12 mins = 720s)
        time_per_slide = 720 / len(chunks) if chunks else 10

        for i, chunk in enumerate(chunks):
            header = Text(f"PHD MODULE | PART {i+1}", color=YELLOW).scale(0.8).to_edge(UP)
            
            # THE BIG FONT: font_size 45 on 720p is massive
            body = Text(chunk, font_size=45, line_spacing=1.5, color=WHITE, alignment="center")
            body.next_to(header, DOWN, buff=0.8)

            self.add(header, body)
            self.wait(time_per_slide)
            self.remove(header, body)

if __name__ == "__main__":
    os.system("manim -ql render_agent.py PhDArchitect --media_dir .")
