# The Writer Agent
lyrics = """
Dil mein teri yaad hai,
In the silence of the night.
Tu hi meri pyas hai,
Everything will be alright.
"""
with open("lyrics.txt", "w") as f:
    f.write(lyrics)
print("✅ Lyrics Written")
