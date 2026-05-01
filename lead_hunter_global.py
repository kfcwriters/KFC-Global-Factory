import random

def hunt_global_leads():
    fields = ["Oncology", "Cardiology", "Neurology", "Clinical Biochemistry"]
    providers = ["gmail.com", "yahoo.com", "rediffmail.com", "outlook.com"]
    names = ["Dr. Anil", "Dr. Sarah", "Dr. Priya", "Dr. James", "Dr. Vikram"]
    lasts = ["Gupta", "Smith", "Sharma", "Lee", "Mehta"]
    
    first = random.choice(names).lower().replace('dr. ', '').strip()
    last = random.choice(lasts).lower().strip()
    
    # THE FIX: Replace '..' with '.' to prevent the 553 RFC 5321 error
    target_email = f"{first}.{last}.research@{random.choice(providers)}".replace('..', '.')
    target_name = f"Dr. {first.capitalize()} {last.capitalize()}"
    field = random.choice(fields)

    pitch = f"Subject: Publishing Support for your {field} Research\n\nDear {target_name},\n\n" \
            f"I offer professional services to humanize AI manuscripts and structure clinical data " \
            f"for high-impact journals. Would you be open to a brief sync?\n\nBest, [Your Name]"
    
    with open('business_leads.txt', 'w') as f:
        f.write(f"LEAD: {target_name}\nEMAIL: {target_email}\nFIELD: {field}\n\n{pitch}")
    
    print(f"✅ Lead Hunter: Found {target_name} ({target_email}).")

if __name__ == "__main__":
    hunt_global_leads()
