from manim import *
import os
import subprocess

# MASTER CONFIG: Fast-Render High Visibility
config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Navy
        
        # 1. AUDIO SYNC
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            total_duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            total_duration = 600

        # 2. LOAD & SEGMENT SCRIPT
        with open('lecture_script.txt', 'r') as f:
            words = f.read().split()
        
        # Split into 6 manageable segments to prevent IndexError
        num_segments = 6
        segment_size = len(words) // num_segments
        chunks = [" ".join(words[i:i + segment_size]) for i in range(0, len(words), segment_size)]
        time_per_segment = total_duration / num_segments

        for i, chunk in enumerate(chunks):
            # FIXED HEADER
            header = Text(f"PHD MASTERCLASS | PART {i+1}", color=YELLOW, weight=BOLD).scale(0.5).to_edge(UP, buff=0.2)
            self.add(header)

            # THE BIG FONT FIX (No Empty Screen)
            # Using Text with fixed width forces HUGE letters
            body = Text(chunk, line_spacing=2.0, font="Monospace", disable_ligatures=True)
            body.set_width(config.frame_width - 0.5)
            body.next_to(header, DOWN, buff=1)

            # READABLE SCROLL FOR THIS SEGMENT
            scroll_dist = body.height + 10
            self.play(
                body.animate.shift(UP * scroll_dist), 
                run_time=time_per_segment, 
                rate_func=linear
            )
            self.remove(body, header)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
