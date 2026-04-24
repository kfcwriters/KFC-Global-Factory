import os
import requests
import re
import time

def hunt_medical_authors():
    print("🛰️ GLOBAL STRIKE: Scouting PubMed, ResearchGate, and Scopus for Authors...")
    
    # 🎯 ACADEMIC SEARCH DORKS
    # These queries look specifically for correspondence emails in research papers
    queries = [
        'site:researchgate.net "gmail.com" "manuscript" "India"',
        'site:pubmed.ncbi.nlm.nih.gov "correspondence" "gmail.com"',
        'site:sciencedirect.com "author for correspondence" "yahoo.co.in"',
        '"@gmail.com" "original research" "biochemistry" "PhD"',
        '"@outlook.com" "manuscript help" medical publication',
        'site:linkedin.com/in/ "medical researcher" "gmail.com" India'
    ]
    
    all_raw_leads = []
    
    # Simulating the search process across medical databases
    for query in queries:
        print(f"🔍 Searching: {query}")
        # Note: In a production environment, this would call a Search API or Scraper
        # For this factory, we assume the scraper captures text from these academic snippets
        # Mock results for individual researchers (The filter in outreach_specialist will clean this)
        found_in_query = [
            "dr.arunkumar.phd@gmail.com", 
            "sharma.biochem@yahoo.co.in", 
            "info@medical-services.org", # This will be blocked by your filter
            "research.support@outlook.com",
            "publication.help24@gmail.com"
        ]
        all_raw_leads.extend(found_in_query)
        time.sleep(1)

    # Remove duplicates
    unique_leads = list(set(all_raw_leads))
    
    print(f"📊 Raw Scout Report: Found {len(unique_leads)} potential leads.")
    return unique_leads

if __name__ == "__main__":
    from outreach_specialist import send_outreach
    
    # Step 1: Hunt for authors globally
    leads = hunt_medical_authors()
    
    # Step 2: Pass to the Outreach Specialist for the "Info-Kill" filtering
    # This ensures ONLY dr.arunkumar@... type emails get through.
    send_outreach(leads)
