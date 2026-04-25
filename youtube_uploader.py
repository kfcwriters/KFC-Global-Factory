import os
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

def create_720p_asset(title, text):
    print(f"🎬 MoviePy Engine: Generating 720p Asset: {title}")
    
    # Create a 5-second 720p background (1280x720)
    bg = ColorClip(size=(1280, 720), color=(0, 0, 50)).set_duration(5)
    
    # Overlay the Clinical Biochemistry text
    txt = TextClip(text, fontsize=50, color='white', size=(1000, 500), method='caption')
    txt = txt.set_position('center').set_duration(5)
    
    final = CompositeVideoClip([bg, txt])
    final.write_videofile("clinical_asset_720p.mp4", fps=24, codec="libx264")
    print("✅ Video Rendered successfully.")

if __name__ == "__main__":
    # Institutional Topic for today
    create_720p_asset("HbA1c Significance", "HbA1c: The Gold Standard in Glycemic Control\nLaboratory Quality Management")
