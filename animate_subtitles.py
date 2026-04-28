from manim import *
import os

config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        
        # 1. Load and Split Script
        with open('lecture_script.txt', 'r') as f:
            words = f.read().split()
        
        # Split into 4 chunks (~250 words each)
        chunks = [" ".join(words[i:i + 250]) for i in range(0, len(words), 250)]

        for i, chunk in enumerate(chunks):
            # Header for each chapter
            header = Text(f"CHAPTER {i+1}", color=YELLOW).scale(0.6).to_edge(UP)
            body = Paragraph(chunk, line_spacing=1.5, alignment="center", width=10).scale(0.7)
            
            self.play(Write(header))
            self.play(FadeIn(body, shift=UP))
            self.wait(20) # Shows the block for 20 seconds
            self.play(FadeOut(body), FadeOut(header))
            self.wait(1)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
