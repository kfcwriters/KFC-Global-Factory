from manim import *
import os

class TeachingMasterclass(Scene):
    def construct(self):
        # 1. Institutional Background
        self.camera.background_color = "#0B1D3A" # Navy Blue
        
        # 2. Load the PhD Script
        if not os.path.exists("lecture_script.txt"):
            text_to_say = "Welcome to the PhD Masterclass on Clinical Biochemistry."
        else:
            with open("lecture_script.txt", "r") as f:
                text_to_say = f.read()[:500] # Focus on the key intro

        # 3. Create Teaching Typography
        title = Text("CLINICAL BIOCHEMISTRY", font="Arial", weight=BOLD).scale(1.2).to_edge(UP)
        subtitle = Text("Sigma Metrics & Quality Management", font="Arial", color=YELLOW).scale(0.8).next_to(title, DOWN)
        
        main_content = Paragraph(
            text_to_say, 
            line_spacing=1.5, 
            alignment="center"
        ).scale(0.6).shift(DOWN*0.5)

        # 4. PROFESSOR ANIMATION
        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP))
        self.wait(1)
        
        # This draws the text word-by-word like a real teacher
        self.play(AddTextLetterByLetter(main_content), run_time=10)
        self.wait(2)
        
        # 5. Outro
        self.play(FadeOut(main_content))
        final_note = Text("RESEARCH CONTINUES...", color=YELLOW).scale(1.2)
        self.play(GrowFromCenter(final_note))
        self.wait(2)

if __name__ == "__main__":
    # Internal command to render the video
    os.system("manim -pql animate_subtitles.py TeachingMasterclass")
