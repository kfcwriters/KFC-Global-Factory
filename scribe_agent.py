import textwrap

def generate_phd_script():
    # In a full run, this pulls from lead_hunter.py
    raw_content = "The integration of Sigma metrics into clinical biochemistry laboratories has redefined analytical quality. By quantifying the performance of assays like HbA1c and Serum Myonectin, we can move beyond traditional QC rules to a risk-based model. This ensures patient safety while optimizing laboratory resources."
    
    # WRAP LOGIC: We force 30 characters per line here so Agent 3 doesn't have to think
    wrapped = "\n".join(textwrap.wrap(raw_content, width=30))
    
    with open('lecture_script.txt', 'w') as f:
        f.write(wrapped)
    print("✅ Agent 1: Script generated and wrapped.")

if __name__ == "__main__":
    generate_phd_script()
