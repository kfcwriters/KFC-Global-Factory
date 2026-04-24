import os
import requests
import re
import time

def hunt_medical_authors():
    print("🛰️ GLOBAL STRIKE: Extracting Real Correspondence Emails from Scopus & PubMed...")
    
    # 🎯 ACADEMIC SEARCH DORKS
    # These queries find people who LITERALLY wrote "email me at..." in their papers
    queries = [
        'site:researchgate.net "corresponding author" "@gmail.com" medical',
        'site:pubmed.ncbi.nlm.nih.gov "email" "@yahoo.com" clinical',
        '"author for correspondence" "@gmail.com" manuscript India',
        'site:nature.com "@gmail.com" biochemistry author'
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    real_emails = []

    for query in queries:
        print(f"🔍 Scraping Academic Snippets: {query}")
        try:
            # We use the Google Search URL to find snippets containing emails
            url = f"https://www.google.com/search?q={query}"
            response = requests.get(url, headers=headers, timeout=10)
            
            # 🧬 THE EXTRACTOR: Finds anything that looks like a real email in the text
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
            
            for e in emails:
                # CEO RULE: Block the generic garbage even at the scraper level
                if not any(x in e.lower() for x in ["info", "admin", "support", "contact", "sales", "google", "example"]):
                    real_emails.append(e.lower())
        except Exception as e:
            print(f"⚠️ Search glitch: {e}")
            
    # Remove duplicates and return
    final_list = list(set(real_emails))
    print(f"📊 SCOUT REPORT: Found {len(final_list)} LIVE academic leads.")
    return final_list

if __name__ == "__main__":
    from outreach_specialist import send_outreach
    leads = hunt_medical_authors()
    send_outreach(leads)
