from manim import *
import os
import subprocess

# MASTER CONFIG: Built for High-Density Readability
config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Institutional Navy
        
        # 1. GET EXACT DURATION
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            total_duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            total_duration = 600

        # 2. LOAD SCRIPT
        with open('lecture_script.txt', 'r') as f:
            words = f.read().split()
        
        # 3. SEGMENTATION: 120 words per slide as requested
        words_per_slide = 120
        chunks = [" ".join(words[i:i + words_per_slide]) for i in range(0, len(words), words_per_slide)]
        time_per_slide = total_duration / len(chunks)

        for i, chunk in enumerate(chunks):
            # Header
            header = Text(f"PHD MASTERCLASS | CHAPTER {i+1}", color=YELLOW, weight=BOLD).scale(0.5).to_edge(UP, buff=0.3)
            self.add(header)

            # THE FONT FIX:
            # - We use Paragraph for better line-breaking
            # - We use scale(1.1) to force it to be much LARGER than the previous run
            # - alignment="center" makes it look like a professional slide
            body = Paragraph(
                chunk, 
                line_spacing=1.2, 
                alignment="center", 
                width=12, # Slightly wider than screen to force larger font scaling
                color=WHITE
            ).scale(1.1) 
            
            # Ensure it fits within the camera frame but remains LARGE
            body.set_width(7.8)
            body.next_to(header, DOWN, buff=0.4)

            # Display logic
            self.add(body)
            self.wait(time_per_slide)
            self.remove(body, header)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
