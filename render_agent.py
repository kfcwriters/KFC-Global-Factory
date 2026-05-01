from manim import *
import os

# MASTER CONFIG: 720p (Perfect for Large Fonts & Stability)
config.pixel_height = 720 
config.pixel_width = 1280
config.frame_rate = 15
config.verbosity = "ERROR"

class PhDArchitect(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Navy
        
        # 1. HEARTBEAT: Ensure script exists
        if not os.path.exists('phd_script.txt'):
            # Fallback text to prevent 2-second crash
            chunks = ["PhD Clinical Biochemistry:", "Advanced Glycated Proteomics Analysis."]
        else:
            with open('phd_script.txt', 'r') as f:
                # Agent 1 uses double newlines to separate slides
                chunks = f.read().split('\n\n')

        # 2. TIMING: 12-minute lecture (720 seconds)
        time_per_slide = 720 / len(chunks) if chunks else 10

        for chunk in chunks:
            # THE FONT FIX:
            # - font_size 45 is giant.
            # - alignment="center" uses the whole horizontal plane.
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
    # FORCE RENDER TO ROOT: This fixes the 'No MP4 found' error
    os.system("manim -ql render_agent.py PhDArchitect --media_dir .")
