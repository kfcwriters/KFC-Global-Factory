#!/usr/bin/env python3
"""
prepare_kaggle.py — Generate lyrics and save to kaggle_music/lyrics.txt
"""
import sys
import os
from pathlib import Path

# Add src/ to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from lyrics_writer import generate_weekly_lyrics
except ImportError:
    print("❌ Could not import lyrics_writer. Make sure src/ exists.")
    sys.exit(1)

def main():
    print("📝 Generating lyrics for Kaggle...")
    
    song = generate_weekly_lyrics()
    sections = song.get("sections", [])
    
    # Build lyrics string from sections
    lyrics_lines = []
    for sec in sections:
        lyrics_lines.extend(sec.get("lines", []))
    lyrics = "\n".join(lyrics_lines)
    
    # Save to kaggle_music/lyrics.txt
    os.makedirs("kaggle_music", exist_ok=True)
    with open("kaggle_music/lyrics.txt", "w") as f:
        f.write(lyrics)
    
    print(f"✅ Lyrics saved to kaggle_music/lyrics.txt ({len(lyrics_lines)} lines)")

if __name__ == "__main__":
    main()
