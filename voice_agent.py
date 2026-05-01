import os
from gtts import gTTS

def generate_voiceover():
    if not os.path.exists('lecture_script.txt'):
        return
        
    with open('lecture_script.txt', 'r') as f:
        text = f.read().replace('\n', ' ')
        words = text.split()[:1200]
    
    # Stability Slice: Generate in two halves
    mid = len(words) // 2
    gTTS(' '.join(words[:mid])).save('p1.mp3')
    gTTS(' '.join(words[mid:])).save('p2.mp3')
    
    # Merge using system FFmpeg
    os.system('ffmpeg -y -i "concat:p1.mp3|p2.mp3" -acodec copy voice.mp3')
    print("✅ Agent 2: Audio voiceover merged and ready.")

if __name__ == "__main__":
    generate_voiceover()
