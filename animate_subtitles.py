from manim import *
import os
import subprocess

# MASTER CONFIG: Fast-Render Academic Display
config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 12 # Low frame rate = High render speed
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Navy
        
        # 1. AUDIO SYNC
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            audio_dur = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            audio_dur = 600

        # 2. LOAD SCRIPT
        with open('lecture_script.txt', 'r') as f:
            full_content = f.read()

        # 3. FIXED HEADER
        header = Text("PHD CLINICAL BIOCHEMISTRY", color=YELLOW, weight=BOLD).scale(0.6).to_edge(UP, buff=0.2)
        self.add(header)

        # 4. THE BIG FONT FIX (No Empty Screen)
        # Using Monospace + disable_ligatures stops the loop in image_a745fb.jpg
        body_text = Text(
            full_content, 
            font="Monospace",
            line_spacing=2.0, 
            disable_ligatures=True
        )

        # FORCE STRETCH: Use the full screen width to make font HUGE
        body_text.set_width(config.frame_width - 0.4)
        body_text.next_to(header, DOWN, buff=1)

        # 5. THE MOTION SCROLL (Zero-Loop Method)
        # We move the block as one single object, not character-by-character
        scroll_dist = body_text.height + 15
        
        self.play(
            body_text.animate.shift(UP * scroll_dist), 
            run_time=audio_dur, 
            rate_func=linear
        )

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
