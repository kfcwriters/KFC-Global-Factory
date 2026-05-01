import textwrap

def scribe_work():
    # Research Topic: Proteomics of Glycated Proteins in Diabetes
    content = (
        "Advanced proteomics now allows us to map the precise sites of protein glycation "
        "in diabetic patients. By identifying these biomarkers early, we can predict "
        "the progression of diabetic nephropathy with high sensitivity. This is the "
        "frontier of clinical biochemistry research today."
    )
    
    # WRAP LOGIC: width=28 forces the text to occupy the full width of a 720p frame
    # We use double newlines to signal "Slides" to Agent 3
    wrapped_slides = textwrap.wrap(content, width=28)
    final_output = "\n\n".join(wrapped_slides)
    
    with open('phd_script.txt', 'w') as f:
        f.write(final_output)
    print("✅ Agent 1: Script pre-wrapped for Massive Font.")

if __name__ == "__main__":
    scribe_work()
