import random

def hunt_global_medical_leads():
    # Global Medical Science Topics 2026
    fields = [
        "Surgical Oncology", "Cardiovascular Medicine", "Pediatric Neurology", 
        "Clinical Biochemistry", "Precision Neurogenomics", "Radiology AI"
    ]
    
    # MIXED DOMAINS: Institutional + Global Personal Providers
    domains = [
        "gmail.com", "yahoo.com", "rediffmail.com", "outlook.com", 
        "aiims.edu", "ox.ac.uk", "hopkinsmedicine.org", "mayo.edu"
    ]
    
    names = ["Dr. Anil", "Dr. Sarah", "Dr. Vikram", "Dr. Linda", "Dr. Priya", "Dr. James"]
    lasts = ["Gupta", "Smith", "Sharma", "Lee", "Mehta", "Vasiliev"]
    
    first = random.choice(names)
    last = random.choice(lasts)
    target_name = f"{first} {last}"
    
    # THE FIX: Pattern rotation to hit different provider types
    provider = random.choice(domains)
    if ".com" in provider:
        # Personal pattern
        target_email = f"{first.lower()}.{last.lower()}.research@{provider}"
    else:
        # Institutional pattern
        target_email = f"clinical.trials@{provider}"
    
    field = random.choice(fields)

    # Professional Outreach Pitch
    pitch = f"""
    Subject: Publication Support for your {field} Manuscript
    
    Dear {target_name},
    
    I noticed your research contributions in the field of {field}. As a fellow 
    scientist specializing in PhD thesis humanization and academic consulting, 
    I offer professional services to help manuscripts pass high-impact peer review.
    
    Our Focus:
    - Humanizing AI-generated academic text to pass rigorous rigor checks.
    - Designing segment-specific molecular panels for clinical data.
    - Systematic review and meta-analysis formatting for Lancet-tier journals.
    
    Are you open to a brief sync on increasing your citation potential?
    
    Best regards,
    [Academic Writing Lead]
    """
    
    with open('business_leads.txt', 'w') as f:
        f.write(f"LEAD: {target_name}\nEMAIL: {target_email}\nFIELD: {field}\n\n{pitch}")
    
    print(f"✅ Lead Hunter: Targeted {target_name} ({target_email}).")

if __name__ == "__main__":
    hunt_global_medical_leads()
