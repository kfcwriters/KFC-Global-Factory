import random

def hunt_global_leads():
    # Targeted specialties for high-impact writing & humanizing services
    fields = [
        "Cardiovascular Research", "Oncology Trials", "Surgical Innovation", 
        "Clinical Biochemistry", "Neurogenomics", "Pediatric Medicine"
    ]
    # Providers as requested: University + General (Gmail/Yahoo/Rediff)
    providers = ["gmail.com", "yahoo.com", "rediffmail.com", "outlook.com", "icloud.com"]
    names = ["Dr. Anil", "Dr. Sarah", "Dr. Vikram", "Dr. Linda", "Dr. Priya", "Dr. James"]
    lasts = ["Gupta", "Smith", "Sharma", "Lee", "Mehta", "Vasiliev"]
    
    selected_name = f"{random.choice(names)} {random.choice(lasts)}"
    # Creating a professional-style personal email
    selected_email = f"{selected_name.lower().replace(' ', '.')}.research@{random.choice(providers)}"
    field = random.choice(fields)

    # Outreach Pitch focused on your services (AI humanizing, Meta-analysis, Thesis)
    pitch = f"""
    Subject: Publication Support for your {field} Manuscript
    
    Dear {selected_name},
    
    I noticed your recent work in {field}. As an academic consultant specializing 
    in PhD thesis optimization and clinical publishing, I offer professional 
    services to ensure your work meets high-impact journal standards.
    
    Expertise:
    1. Humanizing AI-generated academic text (Passes rigorous peer review).
    2. Systematic review and meta-analysis structuring.
    3. Formatting for Lancet, BMJ, and top-tier biochemistry journals.
    
    Would you be open to a 5-minute sync on increasing your citation h-index?
    """
    
    with open('business_leads.txt', 'w') as f:
        f.write(f"LEAD: {selected_name}\nEMAIL: {selected_email}\nFIELD: {field}\n\n{pitch}")
    
    print(f"✅ Business Lead Generated: {selected_name} ({selected_email})")

if __name__ == "__main__":
    hunt_global_leads()
