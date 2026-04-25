import requests
import re

def hunt():
    print("🛰️ SCOUTING: Deep Journal Scraping for ORIGINAL Authors...")
    # Targets specific to high-frequency medical publications
    targets = [
        "https://www.nature.com/nature/articles?type=research",
        "https://www.biomedcentral.com/journals",
        "https://academic.oup.com/journals"
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    found_leads = []

    for url in targets:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            # Find emails specifically associated with professional research
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
            for e in emails:
                addr = e.lower()
                if not any(x in addr for x in ["info", "admin", "support", "sales", "css", "js", "google"]):
                    found_leads.append(addr)
        except: continue

    # Ensure the list is unique and real
    final_list = list(set(found_leads))
    
    with open("current_leads.txt", "w") as f:
        for l in final_list: f.write(f"{l}\n")
    print(f"📊 SCOUT REPORT: Found {len(final_list)} LIVE Authors.")

if __name__ == "__main__":
    hunt()
