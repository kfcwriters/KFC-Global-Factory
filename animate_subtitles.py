from manim import *
import os
import subprocess

# ULTRA-LIGHT CONFIG: Designed to sneak through busy server queues
config.pixel_height = 360 # Reduced resolution for maximum speed
config.pixel_width = 640
config.frame_rate = 10 
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

        # 2. HEADERS
        title = Text("CLINICAL BIOCHEMISTRY", weight=BOLD).scale(0.7).to_edge(UP, buff=0.2)
        subtitle = Text("Sigma Metrics & Quality Management", color=YELLOW).scale(0.4).next_to(title, DOWN, buff=0.1)
        self.add(title, subtitle)

        # 3. SCRIPT LOAD
        with open('lecture_script.txt', 'r') as f:
            full_content = f.read()

        # 4. FAST TELEPROMPTER
        # Text with disable_ligatures=True uses the least possible RAM
        body_text = Text(
            full_content, 
            font_size=24, 
            line_spacing=1.8,
            font="Monospace",
            disable_ligatures=True 
        ).scale(0.7)
        
        body_text.next_to(subtitle, DOWN, buff=0.5)

        # 5. DYNAMIC SCROLL
        scroll_distance = body_text.height + 10
        
        self.play(
            body_text.animate.shift(UP * scroll_distance), 
            run_time=audio_duration, 
            rate_func=linear
        )

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
