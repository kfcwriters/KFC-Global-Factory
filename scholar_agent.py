import random
import textwrap

def generate_deep_script():
    # Focused on your thesis, CBME MBBS curriculum, and MLT Tech
    library = [
        {
            "category": "PHD_THESIS",
            "content": [
                "Advanced proteomics allows us to map precise sites of protein glycation.",
                "In diabetic patients, these biomarkers predict nephropathy progression.",
                "Identifying RBP4 and GPLD1 early is the frontier of clinical research.",
                "Designing segment-specific molecular panels is key to early detection.",
                "This methodology ensures high sensitivity in clinical biochemistry trials."
            ]
        },
        {
            "category": "CBME_MBBS",
            "content": [
                "Gluconeogenesis is the metabolic pathway that generates glucose from non-carbohydrates.",
                "This occurs primarily in the liver during periods of fasting or intense exercise.",
                "Key enzymes like Pyruvate Carboxylase regulate this critical energy flux.",
                "Hormonal control via Glucagon and Insulin ensures blood glucose homeostasis.",
                "Clinical defects in this pathway can lead to severe hypoglycemia and acidosis."
            ]
        },
        {
            "category": "LAB_QUALITY",
            "content": [
                "Sigma metrics quantify laboratory quality by measuring bias and CV.",
                "A Six Sigma process represents world-class quality with minimal defects.",
                "Implementing Westgard Rules ensures analytical performance stays within limits.",
                "Total Laboratory Automation (TLA) reduces pre-analytical errors significantly.",
                "Moving to risk-based QC models optimizes both safety and laboratory cost."
            ]
        }
    ]
    
    selected = random.choice(library)
    
    # Process into narrow slices (22 chars) to force MASSIVE font
    all_slices = []
    for line in selected["content"]:
        # Double wrap ensures we break the text into small "slides"
        all_slices.extend(textwrap.wrap(line, width=22))
    
    # Use double newlines to signal "Slide Changes" to the Master Agent
    with open('phd_script.txt', 'w') as f:
        f.write("\n\n".join(all_slices))
    
    print(f"✅ Scholar Agent: Generated a deep module for {selected['category']}.")

if __name__ == "__main__":
    generate_deep_script()
