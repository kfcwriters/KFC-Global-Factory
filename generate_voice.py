from gtts import gTTS

def make_voice():
    with open("lecture_script.txt", "r") as f:
        script = f.read()
    tts = gTTS(text=script, lang='en')
    tts.save("voice.mp3")
    print("✅ SCRIBE: Voice track generated.")

if __name__ == "__main__":
    make_voice()
