import os
# Fix for MoviePy 2.0 syntax
from moviepy import ColorClip, TextClip, CompositeVideoClip

def create_720p_asset(title, text):
    print(f"🎬 MoviePy 2.0 Engine: Generating 720p Asset: {title}")
    
    # 720p Background (1280x720)
    bg = ColorClip(size=(1280, 720), color=(0, 0, 50)).with_duration(5)
    
    # Clinical Biochemistry text overlay
    # Using 'caption' method for automatic text wrapping
    txt = TextClip(text=text, font_size=50, color='white', size=(1000, 500), method='caption')
    txt = txt.with_position('center').with_duration(5)
    
    final = CompositeVideoClip([bg, txt])
    final.write_videofile("clinical_asset_720p.mp4", fps=24, codec="libx264")
    print("✅ Video Rendered: clinical_asset_720p.mp4")

if __name__ == "__main__":
    # Topic for Science Channel
    create_720p_asset("HbA1c Lab Quality", "HbA1c Monitoring: Gold Standard\nClinical Biochemistry & Sigma Metrics")
