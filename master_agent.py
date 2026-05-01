import os
import subprocess
from gtts import gTTS
from manim import *

# CONFIG: 720p Full-Screen Font
config.pixel_height, config.pixel_width = 720, 1280
config.frame_rate = 15
config.verbosity = "ERROR"

class PhDMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Navy
        
        # 1. READ SCHOLAR'S OUTPUT
        if not os.path.exists('phd_script.txt'):
            return
        with open('phd_script.txt', 'r') as f:
            slides = f.read().split('\n\n')

        # 2. VOICE SYNC
        full_text = " ".join(slides).replace('\n', ' ')
        tts = gTTS(full_text, lang='en', tld='co.in')
        tts.save('phd_voice.mp3')
        
        # Measure duration via ffprobe
        result = subprocess.check_output(
            'ffprobe -i phd_voice.mp3 -show_entries format=duration -v quiet -of csv="p=0"',
            shell=True).decode().strip()
        time_per_slide = float(result) / len(slides)

        # 3. MASSIVE RENDER
        for chunk in slides:
            # Scale 1.6 + weight=BOLD forces screen filling
            txt = Text(chunk, font="Sans", color=WHITE, weight=BOLD).scale(1.6)
            self.add(txt)
            self.wait(time_per_slide)
            self.remove(txt)

if __name__ == "__main__":
    os.system("manim -ql master_agent.py PhDMasterclass --media_dir .")
