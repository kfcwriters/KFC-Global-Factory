import random

def hunt_global_leads():
    # Global medical fields for broad outreach
    fields = ["Oncology", "Cardiology", "Neurology", "Clinical Biochemistry", "Pediatrics"]
    # Including personal and regional email providers
    providers = ["gmail.com", "yahoo.com", "rediffmail.com", "outlook.com", "icloud.com"]
    names = ["Dr. Anil", "Dr. Sarah", "Dr. Priya", "Dr. James", "Dr. Vikram"]
    lasts = ["Gupta", "Smith", "Sharma", "Lee", "Mehta"]
    
    target_name = f"{random.choice(names)} {random.choice(lasts)}"
    # Professional-pattern personal email
    target_email = f"{target_name.lower().replace(' ', '.')}.research@{random.choice(providers)}"
    field = random.choice(fields)

    # Professional outreach pitch for your humanizing & publication services
    pitch = f"""
    Subject: Publication Support for your {field} Research
    
    Dear {target_name},
    
    I noticed your active work in {field}. As a fellow scientist specializing in 
    PhD thesis optimization and academic consulting, I offer professional services 
    to help manuscripts pass high-impact peer review.
    
    Our Focus:
    - Humanizing AI-generated academic text for better rigor.
    - Designing segment-specific clinical data panels.
    - Formatting for Lancet, BMJ, and NEJM standards.
    
    Would you be open to a 5-minute sync on increasing your citation h-index?
    """
    
    with open('business_leads.txt', 'w') as f:
        f.write(f"LEAD: {target_name}\nEMAIL: {target_email}\nFIELD: {field}\n\n{pitch}")
    
    print(f"✅ Business Agent: Generated lead for {target_name} ({target_email}).")

if __name__ == "__main__":
    hunt_global_leads()
