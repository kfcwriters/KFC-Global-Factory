from manim import *
import os

# MASTER CONFIG: 720p Stability
config.pixel_height = 720 
config.pixel_width = 1280
config.frame_rate = 15
config.verbosity = "ERROR"

class PhDArchitect(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Navy
        
        # HEARTBEAT CHECK
        script_path = 'phd_script.txt'
        if not os.path.exists(script_path):
            # Fallback so it doesn't crash in 2 seconds
            chunks = ["Script synchronization in progress...", "Please wait for Agent 1."]
        else:
            with open(script_path, 'r') as f:
                chunks = f.read().split('\n\n')

        # Timing for 12-minute lecture (720s)
        time_per_slide = 720 / len(chunks) if chunks else 10

        for chunk in chunks:
            # THE BIG FONT FIX: 
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
    # Force render to current directory
    os.system("manim -ql render_agent.py PhDArchitect --media_dir .")
