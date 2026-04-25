import requests
import re
import random

def hunt():
    # Expanding keywords to ensure leads are found every run
    keywords = ["Clinical+Biochemistry", "Laboratory+Quality", "Nephropathy", "Biomarkers", "Diabetes+Complications"]
    target = random.choice(keywords)
    page = random.randint(1, 50)
    
    print(f"🛰️ GLOBAL SCOUTING: Targeted PhD Sweep in [{target}] (Page {page})...")
    url = f"https://doaj.org/api/v2/search/articles/{target}?pageSize=100&page={page}"

    try:
        r = requests.get(url, timeout=20)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Filter duplicates and institutional generic mailboxes
        clean = list(set([e.lower() for e in emails if not any(x in e.lower() for x in ["doaj", "info", "support", "noreply"])]))
        
        if clean:
            selected = clean[:20]
            with open("current_leads.txt", "w") as f:
                for m in selected: f.write(f"{m}\n")
            print(f"📊 SCOUT REPORT: {len(selected)} NEW Clinical Specialists identified.")
        else:
            print("⚠️ Sector quiet. Rotating sensors.")
    except Exception as e:
        print(f"⚠️ Hunting Error: {e}")

if __name__ == "__main__":
    hunt()
