import os
from gtts import gTTS

def generate_academic_voice():
    script_path = 'phd_script.txt'
    if not os.path.exists(script_path):
        text = "Welcome to the PhD Masterclass in Clinical Biochemistry."
    else:
        with open(script_path, 'r') as f:
            text = f.read().replace('\n', ' ')

    # Generate voiceover
    tts = gTTS(text, lang='en', tld='co.uk')
    tts.save('phd_voice.mp3')
    print("✅ Agent 2: phd_voice.mp3 generated.")

if __name__ == "__main__":
    generate_academic_voice()
