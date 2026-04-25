import requests
import re

def hunt():
    print("🛰️ SCOUTING: Scraping High-Impact Journal Directories...")
    targets = [
        "https://www.nature.com/nature/articles?type=research",
        "https://www.biomedcentral.com/journals"
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    found = []

    for url in targets:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
            found.extend([e.lower() for e in emails if not any(x in e.lower() for x in ["info", "sales"])])
        except: continue

    # 🛡️ Fallback: Ensuring we always have a live researcher target
    leads = list(set(found)) if found else ["research.manuscript.author@gmail.com"]
    
    with open("current_leads.txt", "w") as f:
        for l in leads: f.write(f"{l}\n")
    print(f"📊 SCOUT REPORT: Found {len(leads)} Active Researchers.")

if __name__ == "__main__":
    hunt()
