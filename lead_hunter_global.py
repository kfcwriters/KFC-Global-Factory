import random

def hunt_global_medical_leads():
    fields = ["Surgical Oncology", "Cardiovascular Medicine", "Pediatric Neurology", "Clinical Biochemistry"]
    domains = ["gmail.com", "yahoo.com", "rediffmail.com", "outlook.com", "aiims.edu", "ox.ac.uk"]
    names = ["Anil Gupta", "Sarah Smith", "Vikram Sharma", "Linda Foster", "Priya Mehta"]
    
    target_name = random.choice(names)
    domain = random.choice(domains)
    
    # Generate clean email based on domain type
    if ".com" in domain:
        target_email = f"{target_name.lower().replace(' ', '.')}@{domain}"
    else:
        target_email = f"research.lead@{domain}"
    
    field = random.choice(fields)

    # Professional Pitch
    pitch_body = f"Dear Dr. {target_name.split()[-1]},\n\nI noticed your research in {field}. I offer professional services to humanize AI manuscripts and structure clinical data for high-impact journals.\n\nAre you open to a brief sync?\n\nBest, Academic Writing Lead"
    
    # SAVING WITH CLEAR LABELS TO PREVENT INDEX ERRORS
    with open('business_leads.txt', 'w') as f:
        f.write(f"TARGET_NAME: {target_name}\n")
        f.write(f"TARGET_EMAIL: {target_email}\n")
        f.write(f"SUBJECT: Professional Publication Support for your {field} Research\n")
        f.write(f"BODY_START\n{pitch_body}")
    
    print(f"✅ Lead Hunter: Targeted {target_name} ({target_email}).")

if __name__ == "__main__":
    hunt_global_medical_leads()
