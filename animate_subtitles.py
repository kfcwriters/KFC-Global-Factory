from manim import *
import os
import subprocess

# HARD CONFIG for GitHub
config.pixel_height = 480 
config.pixel_width = 854
config.frame_rate = 15 
config.verbosity = "ERROR"

class TeachingMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        
        # 1. GET ACTUAL AUDIO DURATION
        # We ask the system how long the 'voice.mp3' actually is
        try:
            cmd = "ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 voice.mp3"
            audio_duration = float(subprocess.check_output(cmd, shell=True).decode().strip())
        except:
            audio_duration = 240 # Fallback to 4 mins if check fails
            
        print(f"🔬 SYNC ENGINE: Audio is {audio_duration}s. Syncing subtitles...")

        # 2. FIXED HEADER
        title = Text("CLINICAL BIOCHEMISTRY", color=WHITE, weight=BOLD).scale(0.8)
        subtitle = Text("Sigma Metrics & Quality Management", color=YELLOW).scale(0.5)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.3)
        self.add(header)

        # 3. LOAD FULL SCRIPT
        try:
            with open('lecture_script.txt', 'r') as f:
                full_content = f.read()
        except:
            full_content = "PhD Lecture Assets Generating..."

        # 4. TELEPROMPTER BODY
        # Using a slightly larger font for readability
        body_text = Text(full_content, font_size=24, line_spacing=1.8).scale(0.7)
        body_text.next_to(header, DOWN, buff=1)

        # 5. THE DYNAMIC SCROLL
        # We calculate the exact distance needed so it doesn't finish early
        scroll_distance = body_text.height + 12 
        
        self.play(
            body_text.animate.shift(UP * scroll_distance), 
            run_time=audio_duration, # LOCKS text speed to audio length
            rate_func=linear
        )
        self.wait(2)

if __name__ == "__main__":
    os.system("manim -ql animate_subtitles.py TeachingMasterclass --media_dir ./media")
