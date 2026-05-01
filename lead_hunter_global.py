import random

def hunt_global_medical_leads():
    fields = ["Surgical Oncology", "Cardiovascular Surgery", "Neurogenomics", "Clinical Biochemistry"]
    providers = ["gmail.com", "yahoo.com", "rediffmail.com", "outlook.com"]
    names = ["Dr. Anil Gupta", "Dr. Sarah Miller", "Dr. Vikram Sharma", "Dr. Linda Chen", "Dr. Priya Mehta"]
    
    target_name = random.choice(names)
    provider = random.choice(providers)
    
    # THE FIX: 
    # 1. Remove 'Dr.' 
    # 2. Replace spaces with dots
    # 3. Strip any dots from the very beginning or end (Fixes .priya.mehta error)
    clean_handle = target_name.lower().replace('dr.', '').strip().replace(' ', '.')
    target_email = f"{clean_handle}@{provider}".replace('..', '.').lstrip('.')
    
    field = random.choice(fields)

    pitch_body = f"""Dear {target_name},

I noticed your specialized work in {field}. As a clinical scientist, I provide premium, 100% manual scientific writing and publication services. 

Our work is strictly human-led, ensuring:
1. Pure Scientific Rigor: Deep logic that AI cannot replicate.
2. Segment-Specific Panels: Manual structuring of clinical data.
3. Journal Compliance: Tailored formatting for Lancet, NEJM, and Nature-tier standards.

We guarantee zero AI-generated content, ensuring your manuscript passes every "AI-Detection" check.

Are you open to a brief sync?

Best regards,
Academic Writing Lead"""
    
    with open('business_leads.txt', 'w') as f:
        f.write(f"TARGET_NAME: {target_name}\n")
        f.write(f"TARGET_EMAIL: {target_email}\n")
        f.write(f"SUBJECT: Manual Expert Publication Support for {field} Research\n")
        f.write(f"BODY_START\n{pitch_body}")
    
    print(f"✅ Sanitized Hunter: Targeted {target_name} ({target_email}).")

if __name__ == "__main__":
    hunt_global_medical_leads()
