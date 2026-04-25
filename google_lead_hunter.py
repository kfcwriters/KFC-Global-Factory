import requests
import re

def hunt():
    print("🛰️ SCOUTING: DOAJ, Copernicus & EMBASE Data Streams...")
    
    # 1. DOAJ API: Targeting 'Clinical Biochemistry'
    doaj_url = "https://doaj.org/api/v2/search/articles/clinical%20biochemistry?pageSize=10"
    
    # 2. Copernicus & EMBASE Scraping Patterns
    web_targets = [
        "https://journals.indexcopernicus.com/search/journal/field?field=7", # Biochemistry field
        "https://www.embase.com/search/quick"
    ]
    
    headers = {"User-Agent": "Mozilla/5.0"}
    found = []

    # Process DOAJ (Highly Reliable)
    try:
        response = requests.get(doaj_url, timeout=10)
        # Extracting emails from the metadata JSON
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
        found.extend(emails)
    except: pass

    # Process Copernicus/EMBASE (Pattern Matching)
    for url in web_targets:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
            found.extend(emails)
        except: continue

    # 🛡️ Cleaning & Filtering
    leads = [e.lower() for e in set(found) if not any(x in e.lower() for x in ["info", "sales", "doaj", "admin"])]

    if leads:
        with open("current_leads.txt", "w") as f:
            for l in leads: f.write(f"{l}\n")
        print(f"📊 SCOUT REPORT: Found {len(leads)} Open Access Researchers.")
    else:
        print("⚠️ No fresh leads from DOAJ/EMBASE this hour.")

if __name__ == "__main__":
    hunt()
