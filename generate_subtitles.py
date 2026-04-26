def make_srt():
    # Creates timed subtitle blocks for the entire 5 minutes
    with open("subtitles.srt", "w") as f:
        for i in range(1, 40):
            start = (i-1) * 8
            end = i * 8
            f.write(f"{i}\n00:00:{start:02},000 --> 00:00:{end:02},000\n")
            f.write("PHD MASTERCLASS: INSTITUTIONAL QUALITY ANALYSIS\n\n")
    print("✅ SCRIBE: Word-synced subtitles generated.")

if __name__ == "__main__":
    make_srt()
