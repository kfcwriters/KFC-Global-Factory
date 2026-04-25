import requests
import re

def hunt():
    print("🛰️ SCOUTING: Broad-Spectrum Global Medical Sweep...")
    
    # Targeting high-value Clinical and Surgical departments
    departments = ["Surgery", "Pathology", "Pediatrics", "Cardiology", "Clinical Biochemistry"]
    all_leads = []

    for dept in departments:
        print(f"🔍 Scanning {dept} researchers...")
        # Increase pageSize to 50 to get more than just 1 email
        url = f"https://doaj.org/api/v2/search/articles/{dept}?pageSize=50"
        try:
            r = requests.get(url, timeout=15)
            # Regex to find all valid email patterns
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
            
            # Filter out junk and institutional generic addresses
            filtered = [e.lower() for e in emails if not any(x in e.lower() for x in ["info", "sales", "doaj", "support", "noreply"])]
            all_leads.extend(filtered)
        except Exception as e:
            print(f"⚠️ Connection interrupted for {dept}: {e}")

    # Remove duplicates and save the mission-critical list
    unique_leads = list(set(all_leads))
    
    if unique_leads:
        with open("current_leads.txt", "w") as f:
            for email in unique_leads:
                f.write(f"{email}\n")
        print(f"📊 SCOUT REPORT: {len(unique_leads)} Medical Scientists identified across all disciplines.")
    else:
        print("⚠️ No new leads found in this cycle. Rotating parameters.")

if __name__ == "__main__":
    hunt()
