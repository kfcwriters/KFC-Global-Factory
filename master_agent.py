import os
import textwrap
import subprocess
from gtts import gTTS
from manim import *

# 1. RESEARCH & WRAP LOGIC
def get_script_content():
    # Focused on your research: Proteomics in Diabetic Nephropathy
    content = ("Advanced proteomics now allows us to map the precise sites of protein glycation "
               "in diabetic patients. By identifying these biomarkers early, we can predict "
               "the progression of diabetic nephropathy with high sensitivity. This is the "
               "frontier of clinical biochemistry research today.")
    # Tight wrap (22 chars) forces MASSIVE font and uses full horizontal screen
    return textwrap.wrap(content, width=22)

# 2. SYNCED RENDERING
config.pixel_height, config.pixel_width = 720, 1280
config.frame_rate = 15
config.verbosity = "ERROR"

class PhDMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Institutional Navy
        slides = get_script_content()
        
        # GENERATE VOICE FIRST TO GET DURATION
        full_text = " ".join(slides)
        tts = gTTS(full_text, lang='en')
        tts.save('phd_voice.mp3')
        
        # MEASURE REAL DURATION
        try:
            result = subprocess.check_output(
                'ffprobe -i phd_voice.mp3 -show_entries format=duration -v quiet -of csv="p=0"',
                shell=True).decode().strip()
            total_duration = float(result)
        except:
            total_duration = len(full_text) / 15 # Fallback estimate
            
        time_per_slide = total_duration / len(slides)

        # RENDER WITH PERFECT SYNC
        for chunk in slides:
            # Huge font (scale 1.5) that hits the screen edges
            txt = Text(chunk, font="Sans", color=WHITE, weight=BOLD).scale(1.5)
            self.add(txt)
            self.wait(time_per_slide)
            self.remove(txt)

if __name__ == "__main__":
    os.system("manim -ql master_agent.py PhDMasterclass --media_dir .")
