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
        
        # 1. Sync
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            total_duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            total_duration = 720

        with open('lecture_script.txt', 'r') as f:
            words = f.read().split()
        
        # 3. 120 Words per slide, but with BOLD LARGE font
        words_per_slide = 120
        chunks = [" ".join(words[i:i + words_per_slide]) for i in range(0, len(words), words_per_slide)]
        time_per_slide = total_duration / len(chunks)

        for i, chunk in enumerate(chunks):
            header = Text(f"CHAPTER {i+1}", color=YELLOW, weight=BOLD).scale(0.5).to_edge(UP, buff=0.3)
            # Alignment center + scale(1.1) fixes the small font issue
            body = Paragraph(chunk, line_spacing=1.3, alignment="center", width=12, color=WHITE).scale(1.1)
            body.set_width(7.6)
            body.next_to(header, DOWN, buff=0.4)

            self.add(header, body)
            self.wait(time_per_slide)
            self.remove(header, body)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
