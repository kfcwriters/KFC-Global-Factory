import requests
import re
import random

def hunt():
    # Searching the broad 'Medicine' term to maximize results
    page = random.randint(1, 100)
    print(f"🛰️ GLOBAL SCOUTING: All Medical Departments (Page {page})...")
    
    url = f"https://doaj.org/api/v2/search/articles/Medicine?pageSize=100&page={page}"

    try:
        r = requests.get(url, timeout=20)
        # Extracting every possible email from the medical journals
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Remove duplicates and known generic junk
        unique = list(set([e.lower() for e in emails if "doaj" not in e.lower()]))
        
        if unique:
            # Taking the top 20 leads for this run
            selected = unique[:20]
            with open("current_leads.txt", "w") as f:
                for mail in selected: f.write(f"{mail}\n")
            print(f"📊 SCOUT REPORT: {len(selected)} NEW Clinical Leads identified.")
        else:
            print("⚠️ No leads in this sector. Rotating page.")
    except Exception as e:
        print(f"⚠️ Hunter Error: {e}")

if __name__ == "__main__":
    hunt()
