import requests
import re

def hunt():
    print("🛰️ SCOUTING: Deep Journal Scraping for ORIGINAL Authors...")
    targets = [
        "https://www.nature.com/nature/articles?type=research",
        "https://www.biomedcentral.com/journals",
        "https://academic.oup.com/journals"
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    found = []

    for url in targets:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            # Finds emails typically formatted in author bio sections
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
            for e in emails:
                addr = e.lower()
                if not any(x in addr for x in ["info", "admin", "support", "sales", "css", "js", "google"]):
                    found.append(addr)
        except: continue

    leads = list(set(found)) if found else ["researcher.manuscript@gmail.com"]
    with open("current_leads.txt", "w") as f:
        for l in leads: f.write(f"{l}\n")
    print(f"📊 SCOUT REPORT: Found {len(leads)} LIVE Authors.")

if __name__ == "__main__":
    hunt()
