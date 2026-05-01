import random

def hunt_leads():
    sectors = ["Diabetes Care", "Wellness Punjab", "Weight Loss Clinic", "Renal Health NGO"]
    target = f"admin.{random.choice(sectors).replace(' ', '').lower()}@gmail.com"
    
    pitch = f"Subject: Scientific Partnership - Dr. Abhishek Bansal\n\nI offer 'Laboratory-First' nutrition protocols for weight loss and diabetes. Are you open to a clinical partnership?"
    
    with open('patient_leads.txt', 'w') as f:
        f.write(f"TARGET: {target}\n{pitch}")

if __name__ == "__main__":
    hunt_leads()
