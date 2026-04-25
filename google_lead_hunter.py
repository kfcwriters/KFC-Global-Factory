import requests
import re

def hunt():
    print("🛰️ SCOUTING: Deep Journal Scraping for LIVE Original Authors...")
    # Targeting high-frequency medical journals directly
    targets = [
        "https://www.nature.com/nature/articles?type=research",
        "https://www.biomedcentral.com/journals",
        "https://academic.oup.com/journals"
    ]
    headers = {"User-Agent": "Mozilla/5.0"}
    found_leads = []

    for url in targets:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            # Pattern to find professional research emails (Edu/Gov/Journal)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
            for e in emails:
                addr = e.lower()
                # Filter out system and tech support emails
                if not any(x in addr for x in ["info", "admin", "support", "sales", "css", "js", "google"]):
                    found_leads.append(addr)
        except: continue

    # Ensure we never send to a placeholder again
    final = list(set(found_leads))
    if not final:
        print("⚠️ No live leads found, skipping outreach to avoid bounces.")
        return

    with open("current_leads.txt", "w") as f:
        for l in final: f.write(f"{l}\n")
    print(f"📊 SCOUT REPORT: Found {len(final)} Active Authors.")

if __name__ == "__main__":
    hunt()
