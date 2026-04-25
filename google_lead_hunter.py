import requests
import re
import os

def hunt():
    print("🛰️ SCOUTING: Total-Field Global Medical Sweep (Every Specialty)...")
    
    # "LCC:R" is the global code for ALL Medicine (Surgery, Neuro, Cardio, etc.)
    url = "https://doaj.org/api/v2/search/articles/bibjson.subject.term:Medicine?pageSize=100"
    
    # History tracking to ensure zero repetition
    history_file = "sent_history.txt"
    sent_emails = []
    if os.path.exists(history_file):
        with open(history_file, "r") as h:
            sent_emails = [line.strip() for line in h.readlines()]

    try:
        r = requests.get(url, timeout=20)
        # Deep extraction of all email patterns
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
        
        # Filter: No duplicates, no previous contacts, no junk
        new_leads = []
        for e in set(emails):
            e_low = e.lower()
            if e_low not in sent_emails and not any(x in e_low for x in ["info", "doaj", "support", "noreply", "sales"]):
                new_leads.append(e_low)

        # Selection: Taking the top 15 fresh leads across all fields
        selected = new_leads[:15]
        
        if selected:
            with open("current_leads.txt", "w") as f:
                for mail in selected: f.write(f"{mail}\n")
            
            with open(history_file, "a") as h:
                for mail in selected: h.write(f"{mail}\n")
                
            print(f"📊 SCOUT REPORT: {len(selected)} NEW Researchers found in the Total Medical Sweep.")
        else:
            print("⚠️ No new leads in this specific sector. Refreshing scan...")
    except Exception as e:
        print(f"⚠️ Hunting Error: {e}")

if __name__ == "__main__":
    hunt()
