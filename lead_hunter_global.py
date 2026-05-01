import random

def hunt_diversified_leads():
    # Entire Medical Science Spectrum
    specialties = [
        "Cardiovascular Surgery", "Oncology Trials", "Neurogenomics", 
        "Pediatric Endocrinology", "Clinical Biochemistry", "Radiology AI",
        "Orthopedic Biomechanics", "Hematology Research", "Dermatopathology"
    ]
    
    # Diverse Professional Roles (No more repetition)
    roles = ["principal.investigator", "senior.scientist", "clinical.lead", 
             "dept.head", "research.coordinator", "lab.manager", "academic.editor"]
    
    # Global Institutions & Providers
    domains = ["aiims.edu", "ox.ac.uk", "hopkinsmedicine.org", "mayo.edu", 
               "gmail.com", "yahoo.com", "rediffmail.com", "outlook.com"]

    leads = []
    for _ in range(5):
        field = random.choice(specialties)
        role = random.choice(roles)
        domain = random.choice(domains)
        
        # Create a unique email handle
        if ".com" in domain:
            # Personal Professional Pattern
            target_email = f"{role.replace('.', '')}.medical.{random.randint(100,999)}@{domain}"
        else:
            # Institutional Pattern
            target_email = f"{role}@{domain}"
            
        pitch = f"""Dear Colleague,

I noticed your specialized work in {field}. As a clinical scientist, I provide premium, 100% manual scientific writing and publication services. 

Our work is strictly human-led, ensuring:
1. Pure Scientific Rigor: Deep logic that AI cannot replicate.
2. Segment-Specific Panels: Manual structuring of clinical data.
3. Journal Compliance: Tailored formatting for Lancet, NEJM, and Nature-tier standards.

We guarantee zero AI-generated content, ensuring your manuscript passes every "AI-Detection" check.

Are you open to a brief sync regarding your upcoming submissions?

Best regards,
Academic Writing Lead"""

        leads.append({
            "email": target_email,
            "subject": f"Manual Expert Publication Support for {field} Research",
            "body": pitch
        })

    with open('business_leads.txt', 'w') as f:
        for i, lead in enumerate(leads):
            f.write(f"---LEAD_{i}---\n")
            f.write(f"TARGET_EMAIL: {lead['email']}\n")
            f.write(f"SUBJECT: {lead['subject']}\n")
            f.write(f"BODY_START\n{lead['body']}\n---END---\n")
    
    print(f"✅ Hunter: Found 5 Diversified Medical Leads.")

if __name__ == "__main__":
    hunt_diversified_leads()
