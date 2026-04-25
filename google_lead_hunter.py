import requests
import re
import random

def hunt():
    print("🛰️ GLOBAL SCOUTING: All Specialty Sweep...")
    # Using a broader query and random page to force new leads
    page = random.randint(1, 40)
    url = f"https://doaj.org/api/v2/search/articles/Medicine?pageSize=100&page={page}"

    try:
        r = requests.get(url, timeout=20)
        # Pulling every email from the global medical database
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Filter for unique addresses, ignoring common platform emails
        clean = list(set([e.lower() for e in emails if "doaj" not in e.lower()]))
        
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
