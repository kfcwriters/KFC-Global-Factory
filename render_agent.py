from manim import *
import os

class PhDArchitect(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        
        # Load pre-wrapped script from Agent 1
        with open('phd_script.txt', 'r') as f:
            chunks = f.read().split('\n\n')

        for i, chunk in enumerate(chunks):
            # THE BIG FONT: font_size 42 on 720p is massive
            text = Text(chunk, font_size=42, line_spacing=1.5, color=WHITE, alignment="center")
            self.add(text)
            self.wait(6) # Sync with Agent 2 timing
            self.remove(text)
