import requests
import re

def hunt():
    print("🛰️ SCOUTING: DOAJ, Copernicus & EMBASE Data Streams...")
    # Direct metadata search for Biochemistry
    doaj_url = "https://doaj.org/api/v2/search/articles/clinical%20biochemistry?pageSize=15"
    headers = {"User-Agent": "Mozilla/5.0"}
    found = []

    try:
        r = requests.get(doaj_url, timeout=10)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        found.extend([e.lower() for e in emails if not any(x in e.lower() for x in ["info", "sales", "doaj"])])
    except: pass

    # 🛡️ Persistence Check
    if found:
        with open("current_leads.txt", "w") as f:
            for l in set(found): f.write(f"{l}\n")
        print(f"📊 SCOUT REPORT: Found {len(set(found))} Open Access Authors.")
    else:
        print("⚠️ No fresh leads this hour. Standing by.")

if __name__ == "__main__":
    hunt()
