from manim import *
import os

# MASTER CONFIG: 720p for Stability
config.pixel_height = 720 
config.pixel_width = 1280
config.frame_rate = 15
config.verbosity = "ERROR"

class PhDArchitect(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Navy
        
        # Load the pre-wrapped scripts from Agent 1
        script_file = 'phd_script.txt'
        if not os.path.exists(script_file):
            return

        with open(script_file, 'r') as f:
            # We split by double newlines to create distinct "Slides"
            chunks = f.read().split('\n\n')

        # Total duration for a PhD module (720 seconds / 12 mins)
        time_per_slide = 720 / len(chunks) if chunks else 10

        for chunk in chunks:
            if not chunk.strip(): continue
            
            # THE BIG FONT: font_size 45 on 720p is physically massive
            # alignment="center" ensures it fills the horizontal plane
            text = Text(
                chunk.strip(), 
                font_size=45, 
                line_spacing=1.5, 
                color=WHITE, 
                alignment="center"
            )
            
            self.add(text)
            self.wait(time_per_slide)
            self.remove(text)

if __name__ == "__main__":
    # Force render to current directory so Agent 4 can find it
    os.system("manim -ql render_agent.py PhDArchitect --media_dir .")
