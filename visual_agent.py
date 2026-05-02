from manim import *

class VisualShort(Scene):
    def construct(self):
        bg = FullScreenRectangle(fill_opacity=1).set_color("#1A0F0F")
        self.add(bg)
        
        frame = SurroundingRectangle(FullScreenRectangle(), color="#D4AF37", buff=-0.5)
        title = Text("VELVET HOURS", font="Sans", size=0.6, color="#D4AF37").to_edge(UP)
        
        self.play(FadeIn(bg), Create(frame), Write(title), run_time=3)
        self.play(Indicate(title), run_time=5)
        self.wait(17)
