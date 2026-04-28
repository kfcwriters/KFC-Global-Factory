from manim import *
import os
import subprocess

# EMPEROR SPEED CONFIG
config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15 
config.verbosity = "ERROR" 

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" 
        
        # 1. AUDIO SYNC
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            audio_duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            audio_duration = 300 

        # 2. BRANDING
        title = Text("CLINICAL BIOCHEMISTRY", weight=BOLD).scale(0.8).to_edge(UP, buff=0.3)
        subtitle = Text("Sigma Metrics & Quality Management", color=YELLOW).scale(0.5).next_to(title, DOWN)
        self.add(title, subtitle)

        # 3. LOAD 800-WORD SCRIPT
        with open('lecture_script.txt', 'r') as f:
            full_content = f.read()

        # 4. THE TURBO SUBTITLE WAY (Tex Method)
        # We wrap the text so it fits the screen width (width=6.5)
        # Using Tex() instead of Text() prevents the loop in image_23c515.png
        body_text = Tex(
            r"\begin{flushleft} " + full_content + r" \end{flushleft}",
            tex_environment=None,
            color=WHITE,
            font_size=28
        ).scale(0.8).set_width(7)
        
        body_text.next_to(subtitle, DOWN, buff=1)

        # 5. DYNAMIC SCROLL
        scroll_distance = body_text.height + 15
        
        self.play(
            body_text.animate.shift(UP * scroll_distance), 
            run_time=audio_duration, 
            rate_func=linear
        )
        self.wait(1)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
