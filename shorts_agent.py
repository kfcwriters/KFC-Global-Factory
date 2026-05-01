from manim import *
import random

class YouTubeShorts(Scene):
    def construct(self):
        # Setting vertical resolution for YouTube Shorts
        config.pixel_height = 1920
        config.pixel_width = 1080
        config.frame_height = 16.0
        config.frame_width = 9.0

        facts = [
            "100% HUMAN EXPERTISE\nIS THE ONLY WAY\nTO PASS PEER REVIEW.",
            "STOP USING AI FOR\nMEDICAL RESEARCH.\nUSE MANUAL LOGIC.",
            "SIGMA METRICS TIP:\nCONSISTENCY IS KEY\nIN CLINICAL LABS."
        ]
        
        text = Text(random.choice(facts), font_size=90, color=YELLOW, weight=BOLD)
        text.width = 8
        self.play(FadeIn(text, shift=UP))
        self.wait(3)
        self.play(FadeOut(text, shift=DOWN))
