import random
import textwrap

def generate_dynamic_script():
    # DATABASE: Rotating between Thesis Writing, CBME MBBS topics, and MLT Tech
    library = {
        "THESIS_WRITING": [
            "Methodology: Designing a segment-specific molecular panel for Diabetic Nephropathy.",
            "Thesis Structure: How to humanize AI-generated discussions while maintaining academic rigor.",
            "Grant Writing: Navigating ICMR Extra-Mural project frameworks for clinical scientists.",
            "Ethics in Research: The importance of patient consent in clinical biochemistry datasets."
        ],
        "CBME_MBBS": [
            "Metabolism: The hormonal regulation of Gluconeogenesis in the fasting state.",
            "Clinical Correlation: Understanding the anion gap in Metabolic Acidosis (ABG Analysis).",
            "Enzymology: Competitive vs Non-competitive inhibition in drug design (Statins example).",
            "Organ Function: Interpreting Liver Function Tests (LFT) in Obstructive Jaundice."
        ],
        "MLT_LAB_TECH": [
            "Automation: The shift from manual assays to Total Laboratory Automation (TLA).",
            "Quality Control: Implementing Westgard Rules and Sigma metrics in high-volume labs.",
            "Point of Care: Troubleshooting glucometer variance in clinical ward settings.",
            "Pre-analytical Errors: Impact of hemolysis and lipemia on spectrophotometric results."
        ]
    }

    # PICK CATEGORY & TOPIC
    category = random.choice(list(library.keys()))
    topic = random.choice(library[category])
    
    # FORMAT FOR MASSIVE FONT: Wrap at 22 chars
    # We use double newlines to signal "Slides" to the Master Agent
    wrapped_content = "\n\n".join(textwrap.wrap(topic, width=22))
    
    with open('phd_script.txt', 'w') as f:
        f.write(wrapped_content)
    
    print(f"✅ Scholar Agent: Generated a {category} script.")

if __name__ == "__main__":
    generate_dynamic_script()
