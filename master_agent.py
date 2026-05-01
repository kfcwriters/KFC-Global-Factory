import os
import textwrap
import subprocess
import random
from gtts import gTTS
from manim import *

# 1. DYNAMIC RESEARCH AGENT
def get_random_phd_topic():
    topics = [
        "The role of RBP4 and GPLD1 as novel biomarkers for predicting the onset of Diabetic Nephropathy.",
        "How Sigma Metrics revolutionize laboratory quality management by quantifying analytical performance.",
        "The impact of mitoprotective drugs like Miglustat on Rotenone-induced toxicity in SH-SY5Y cell lines.",
        "Analyzing the proteomics of glycated proteins to identify early-stage diabetic kidney disease.",
        "The transition from traditional QC rules to risk-based analytical models in clinical biochemistry.",
        "Investigating circulating serum myonectin levels as a metabolic regulator in Type 2 Diabetes."
    ]
    content = random.choice(topics)
    # Tight wrap (20-22 chars) forces MASSIVE font and full horizontal coverage
    return textwrap.wrap(content, width=22)

# 2. SYNCHRONIZED RENDERING
config.pixel_height, config.pixel_width = 720, 1280
config.frame_rate = 15
config.verbosity = "ERROR"

class PhDMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A" # Navy
        slides = get_random_phd_topic()
        
        # Audio Generation
        full_text = " ".join(slides)
        tts = gTTS(full_text, lang='en', tld='co.in')
        tts.save('phd_voice.mp3')
        
        # MEASURE AUDIO DURATION (The Alignment Fix)
        try:
            result = subprocess.check_output(
                'ffprobe -i phd_voice.mp3 -show_entries format=duration -v quiet -of csv="p=0"',
                shell=True).decode().strip()
            total_duration = float(result)
        except:
            total_duration = len(full_text) / 14 
            
        duration_per_slide = total_duration / len(slides)

        # RENDER WITH DYNAMIC FONT
        for chunk in slides:
            # Scale 1.6 ensures the text hits the margins
            txt = Text(chunk, font="Sans", color=WHITE, weight=BOLD).scale(1.6)
            self.add(txt)
            self.wait(duration_per_slide)
            self.remove(txt)

if __name__ == "__main__":
    os.system("manim -ql master_agent.py PhDMasterclass --media_dir .")
