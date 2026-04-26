import requests
import re
import random

def hunt():
    print("🛰️ INSTITUTIONAL SCOUT: Universal Medical Sweep...")
    # Using the broadest possible medical terms to guarantee hits
    keywords = ["Medicine", "Clinical", "Biomedical", "Healthcare", "Research"]
    target = random.choice(keywords)
    page = random.randint(1, 150)
    
    url = f"https://doaj.org/api/v2/search/articles/{target}?pageSize=100&page={page}"

    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Filtering for unique academic leads
        clean = list(set([e.lower() for e in emails if not any(x in e.lower() for x in ["doaj", "info", "support"])]))
        
        if clean:
            selected = clean[:25]
            with open("current_leads.txt", "w") as f:
                for mail in selected: f.write(f"{mail}\n")
            print(f"📊 SCOUT REPORT: {len(selected)} NEW Research Leads identified.")
        else:
            print("⚠️ Sector quiet. Rotating sensors for next sweep.")
    except Exception as e:
        print(f"⚠️ Hunter Error: {e}")

if __name__ == "__main__":
    hunt()
