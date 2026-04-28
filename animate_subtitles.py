from manim import *
import os
import subprocess

# SPEED CONFIG: Fast render for long PhD scripts
config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15 
config.verbosity = "ERROR" # Stops the repeating logs from image_32cc19.jpg

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        
        # 1. GET EXACT DURATION
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            audio_duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            audio_duration = 300 

        # 2. FIXED HEADER
        title = Text("CLINICAL BIOCHEMISTRY", weight=BOLD).scale(0.8).to_edge(UP, buff=0.3)
        subtitle = Text("Sigma Metrics & Quality Management", color=YELLOW).scale(0.5).next_to(title, DOWN)
        self.add(title, subtitle)

        # 3. LOAD 1000-WORD SCRIPT
        with open('lecture_script.txt', 'r') as f:
            full_content = f.read()

        # 4. THE SUBTITLE BLOCK
        # 'disable_ligatures' is the secret—it stops the line-by-line log processing
        body_text = Text(
            full_content, 
            font_size=22, 
            line_spacing=1.8,
            disable_ligatures=True 
        ).scale(0.7)
        
        body_text.next_to(subtitle, DOWN, buff=1)

        # 5. DYNAMIC SCROLL
        scroll_distance = body_text.height + 15
        
        # We use a simple shift. No 'Write' or 'Fade' to save CPU
        self.play(
            body_text.animate.shift(UP * scroll_distance), 
            run_time=audio_duration, 
            rate_func=linear
        )

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
