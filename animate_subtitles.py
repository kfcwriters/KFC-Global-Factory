from manim import *
import os
import subprocess

# MASTER CONFIG: Fast & Clear
config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        
        # 1. Get Exact Audio Duration
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            total_duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            total_duration = 720 # 12 mins fallback

        # 2. Load Script
        with open('lecture_script.txt', 'r') as f:
            words = f.read().split()
        
        # 3. SEGMENTATION: 40 words per slide for maximum font size
        words_per_slide = 40
        chunks = [" ".join(words[i:i + words_per_slide]) for i in range(0, len(words), words_per_slide)]
        time_per_slide = total_duration / len(chunks)

        for i, chunk in enumerate(chunks):
            # Header - Small and at the top
            header = Text(f"PART {i+1}", color=YELLOW, weight=BOLD).scale(0.5).to_edge(UP, buff=0.2)
            
            # THE FONT FIX: Large, readable, and wrapped
            # We use a fixed font_size=36 to ensure it's big enough for Telegram
            body = Text(chunk, font_size=36, line_spacing=1.5, t2c={chunk: WHITE}).scale(0.8)
            
            # Wrap the text manually by width
            if body.width > 7:
                body.set_width(7.5)
            
            body.next_to(header, DOWN, buff=0.5)

            # High-Speed Display
            self.add(header, body)
            self.wait(time_per_slide)
            self.remove(header, body)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
