from manim import *
import os
import textwrap

# MASTER CONFIG: 720p (Maximum Stability)
config.pixel_height = 720 
config.pixel_width = 1280
config.frame_rate = 15
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Institutional Navy
        
        # 1. ASSET SYNC
        script_path = 'lecture_script.txt'
        if not os.path.exists(script_path):
            # Safe fallback text to prevent crash
            script_text = "Masterclass: Sigma Metrics in Clinical Biochemistry. Optimizing laboratory quality."
        else:
            with open(script_path, 'r') as f:
                script_text = f.read()
        
        # 2. SEGMENTATION: 30 words per slide for MASSIVE Visibility
        words = script_text.split()
        chunk_size = 30 
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        
        # Calculate timing for 12-minute video (720 seconds)
        time_per_slide = 720 / len(chunks) if len(chunks) > 0 else 10

        for i, chunk in enumerate(chunks):
            # HEADER
            header = Text(f"PHD MASTERCLASS | PART {i+1}", color=YELLOW, weight=BOLD).scale(0.8).to_edge(UP, buff=0.4)
            
            # THE FONT FIX:
            # - Wrap width 35 forces text to expand horizontally
            # - font_size 42 is huge and readable on mobile
            # - alignment="center" removes empty screen space
            wrapped_text = "\n".join(textwrap.wrap(chunk, width=35))
            body = Text(
                wrapped_text, 
                font_size=42, 
                line_spacing=1.5, 
                color=WHITE,
                alignment="center" 
            )
            
            body.next_to(header, DOWN, buff=0.6)

            # RENDER: Static Page-Turn
            self.add(header, body)
            self.wait(time_per_slide)
            self.remove(header, body)

if __name__ == "__main__":
    # Explicitly render to current directory to avoid folder permission errors
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir .")
