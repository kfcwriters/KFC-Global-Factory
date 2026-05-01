import random

def hunt_global_leads():
    # Targeted specialties for high-impact writing services
    fields = ["Oncology", "Cardiology", "Neurogenomics", "Clinical Biochemistry", "Pediatrics"]
    providers = ["gmail.com", "yahoo.com", "rediffmail.com", "outlook.com"]
    names = ["Dr. Anil", "Dr. Sarah", "Dr. Vikram", "Dr. Linda", "Dr. Priya", "Dr. James"]
    lasts = ["Gupta", "Smith", "Sharma", "Lee", "Mehta", "Vasiliev"]
    
    target_name = f"{random.choice(names)} {random.choice(lasts)}"
    # Generate Gmail/Yahoo/Rediff style email for outreach
    target_email = f"{target_name.lower().replace(' ', '.')}.research@{random.choice(providers)}"
    field = random.choice(fields)

    # The exact format the email_sender.py will parse
    pitch = f"Subject: Professional Publication Support for your {field} Manuscript\n\n" \
            f"Dear {target_name},\n\n" \
            f"I am an academic consultant specializing in PhD thesis optimization and high-impact " \
            f"medical publishing. I noticed your recent work in {field} and would like to offer " \
            f"professional assistance in humanizing AI-generated academic text and structuring " \
            f"clinical data panels for peer review.\n\n" \
            f"Our services ensure your manuscripts meet the rigorous standards of journals like " \
            f"The Lancet and BMJ. Are you open to a brief sync regarding your upcoming submissions?\n\n" \
            f"Best regards,\n[Academic Writing Lead]"
    
    with open('business_leads.txt', 'w') as f:
        f.write(f"LEAD: {target_name}\nEMAIL: {target_email}\nFIELD: {field}\n\n{pitch}")
    
    print(f"✅ Lead Hunter: Targeted {target_name} ({target_email}).")

if __name__ == "__main__":
    hunt_global_leads()
