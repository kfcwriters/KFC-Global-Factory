import os
import textwrap
from gtts import gTTS
from manim import *

# 1. SCHOLAR AGENT: Research & Wrap
def get_script():
    content = ("Advanced proteomics now allows us to map the precise sites of protein glycation "
               "in diabetic patients. By identifying these biomarkers early, we can predict "
               "the progression of diabetic nephropathy with high sensitivity.")
    return "\n\n".join(textwrap.wrap(content, width=25))

# 2. ORATOR AGENT: Voice
def make_voice(text):
    tts = gTTS(text.replace('\n', ' '), lang='en')
    tts.save('phd_voice.mp3')

# 3. ARCHITECT AGENT: Rendering
config.pixel_height, config.pixel_width = 720, 1280
config.frame_rate = 15
config.verbosity = "ERROR"

class PhDMasterclass(Scene):
    def construct(self):
        self.camera.background_color = "#0B1D3A"
        script = get_script()
        chunks = script.split('\n\n')
        
        for chunk in chunks:
            # We use 'Text' with a scale to bypass the Paragraph/Pango system font crash
            txt = Text(chunk, font="Sans", color=WHITE).scale(1.2)
            self.add(txt)
            self.wait(5)
            self.remove(txt)

if __name__ == "__main__":
    script_text = get_script()
    make_voice(script_text)
    # Force render to current directory
    os.system("manim -ql master_agent.py PhDMasterclass --media_dir .")
