import requests
import re
import random

def hunt():
    # Diversified medical departments to ensure a 100% success rate
    sectors = ["Medicine", "Clinical+Research", "Surgery", "Oncology", "Pathology"]
    target = random.choice(sectors)
    page = random.randint(1, 50)
    
    print(f"🛰️ GLOBAL SCOUTING: All Specialty Sweep in [{target}] (Page {page})...")
    url = f"https://doaj.org/api/v2/search/articles/{target}?pageSize=100&page={page}"

    try:
        r = requests.get(url, timeout=20)
        # Extracting every possible email from the research papers
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Filter: Remove duplicates and common non-researcher addresses
        clean = list(set([e.lower() for e in emails if not any(x in e.lower() for x in ["doaj", "info", "support", "noreply"])]))
        
        if clean:
            # Taking a batch of 20 high-value leads
            selected = clean[:20]
            with open("current_leads.txt", "w") as f:
                for m in selected: f.write(f"{m}\n")
            print(f"📊 SCOUT REPORT: {len(selected)} NEW Specialists identified.")
        else:
            print("⚠️ Sector quiet. Rotating sensors to alternate medical branch.")
    except Exception as e:
        print(f"⚠️ Hunting Error: {e}")

if __name__ == "__main__":
    hunt()
