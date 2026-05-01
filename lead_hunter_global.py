import random

def hunt_global_medical_leads():
    fields = [
        "Surgical Oncology", "Cardiovascular Surgery", "Neurogenomics", 
        "Clinical Biochemistry", "Pediatric Endocrinology", "Radiology"
    ]
    domains = ["gmail.com", "yahoo.com", "rediffmail.com", "outlook.com", "aiims.edu", "ox.ac.uk"]
    names = ["Dr. Anil Gupta", "Dr. Sarah Miller", "Dr. Vikram Sharma", "Dr. Linda Chen", "Dr. Priya Mehta"]
    
    target_name = random.choice(names)
    domain = random.choice(domains)
    
    # Generate clean email address
    if ".com" in domain:
        target_email = f"{target_name.lower().replace(' ', '.').replace('dr.', '')}@{domain}".replace('..', '.')
    else:
        target_email = f"clinical.research@{domain}"
    
    field = random.choice(fields)

    # NEW PITCH: Emphasizing 100% Human, No-AI Expertise
    pitch_body = f"""Dear {target_name},

I noticed your specialized work in {field}. As a clinical scientist, I provide premium, 100% manual scientific writing and publication services. 

Unlike automated tools, our work is strictly human-led, ensuring:
1. Pure Scientific Rigor: Deep logic that AI cannot replicate.
2. Segment-Specific Panels: Manual structuring of complex clinical data.
3. Journal Compliance: Tailored formatting for Lancet, NEJM, and Nature-tier standards.

We guarantee zero AI-generated content, ensuring your manuscript passes every "AI-Detection" check during peer review. 

Are you open to a brief sync regarding your upcoming submissions?

Best regards,
Academic Writing Lead"""
    
    # Standardized saving logic for the sender
    with open('business_leads.txt', 'w') as f:
        f.write(f"TARGET_NAME: {target_name}\n")
        f.write(f"TARGET_EMAIL: {target_email}\n")
        f.write(f"SUBJECT: Manual Expert Publication Support for {field} Research\n")
        f.write(f"BODY_START\n{pitch_body}")
    
    print(f"✅ Human-Led Hunter: Targeted {target_name} ({target_email}).")

if __name__ == "__main__":
    hunt_global_medical_leads()
