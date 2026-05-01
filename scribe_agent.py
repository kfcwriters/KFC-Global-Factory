import textwrap
import os

def generate_academic_content():
    # Research: Proteomics of Glycated Proteins in Diabetes
    topic = (
        "Advanced proteomics now allows us to map the precise sites of protein glycation "
        "in diabetic patients. By identifying these biomarkers early, we can predict "
        "the progression of diabetic nephropathy with high sensitivity. This is the "
        "frontier of clinical biochemistry research today."
    )
    
    # WRAP LOGIC: width=28 forces the text to occupy the full width of a 720p frame
    # We use double newlines to signal "Slides" to Agent 3
    wrapped_slides = textwrap.wrap(topic, width=28)
    final_output = "\n\n".join(wrapped_slides)
    
    # Force writing to the current working directory
    with open('phd_script.txt', 'w') as f:
        f.write(final_output)
    
    if os.path.exists('phd_script.txt'):
        print("✅ Agent 1: Script verified at root.")

if __name__ == "__main__":
    generate_academic_content()
