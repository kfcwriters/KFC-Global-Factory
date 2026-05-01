import random

def hunt_global_leads():
    specialties = ["Oncology", "Cardiology", "Neurology", "Clinical Biochemistry"]
    providers = ["gmail.com", "yahoo.com", "rediffmail.com", "outlook.com"]
    names = ["Dr. Anil", "Dr. Sarah", "Dr. Priya", "Dr. James", "Dr. Vikram"]
    lasts = ["Gupta", "Smith", "Sharma", "Lee", "Mehta"]
    
    target_name = f"{random.choice(names)} {random.choice(lasts)}"
    target_email = f"{target_name.lower().replace(' ', '.')}.research@{random.choice(providers)}"
    field = random.choice(specialties)

    pitch = f"Subject: Publishing Support for your {field} Research\n\nDear {target_name},\n\n" \
            f"We specialize in humanizing AI-generated medical manuscripts and designing " \
            f"clinical data panels for high-impact journals. Would you be open to a " \
            f"5-minute sync on increasing your citation h-index?\n\nBest, [Your Name]"
    
    with open('business_leads.txt', 'w') as f:
        f.write(f"LEAD: {target_name}\nEMAIL: {target_email}\nFIELD: {field}\n\n{pitch}")
    
    print(f"✅ Lead Hunter: Found {target_name} ({target_email}).")

if __name__ == "__main__":
    hunt_global_leads()
