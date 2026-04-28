from manim import *
import os
import subprocess

config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        
        # 1. Sync Logic
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            total_duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            total_duration = 600

        # 2. Load Script
        with open('lecture_script.txt', 'r') as f:
            words = f.read().split()
        
        # Split into 5 Chapters for better readability
        chunk_size = len(words) // 5
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        time_per_chapter = total_duration / 5

        for i, chunk in enumerate(chunks):
            # Header
            header = Text(f"CHAPTER {i+1}: PhD Insights", color=YELLOW, weight=BOLD).scale(0.7).to_edge(UP, buff=0.3)
            self.add(header)

            # LARGE READABLE TEXT (Fixes the issue in image_21f759.jpg)
            body = Text(chunk, line_spacing=2.0, font_size=32).scale(0.8)
            body.next_to(header, DOWN, buff=1)

            # Scroll each chapter
            scroll_dist = body.height + 10
            self.play(
                body.animate.shift(UP * scroll_dist), 
                run_time=time_per_chapter, 
                rate_func=linear
            )
            self.remove(body, header)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
