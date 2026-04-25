import requests
import re
import random

def hunt():
    print("🛰️ GLOBAL SCOUTING: Deep-Crawl Specialty Sweep...")
    
    # We rotate through highly specific clinical sectors to find fresh emails
    specialties = [
        "Cardiology", "Neurology", "Gastroenterology", "Immunology", 
        "Dermatology", "Endocrinology", "Nephrology", "Oncology"
    ]
    target = random.choice(specialties)
    
    # Using a high page-offset to find older but active researchers
    page = random.randint(50, 150)
    url = f"https://doaj.org/api/v2/search/articles/{target}?pageSize=100&page={page}"

    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Filtering for unique academic and clinical leads
        clean = list(set([e.lower() for e in emails if not any(x in e.lower() for x in ["doaj", "info", "support"])]))
        
        if clean:
            selected = clean[:25]
            with open("current_leads.txt", "w") as f:
                for mail in selected: f.write(f"{mail}\n")
            print(f"📊 SCOUT REPORT: {len(selected)} NEW {target} Specialists identified.")
        else:
            print(f"⚠️ {target} sector quiet. Re-routing to alternate specialty.")
    except Exception as e:
        print(f"⚠️ Hunter Error: {e}")

if __name__ == "__main__":
    hunt()
