import os
import requests

def hunt_authors():
    # 🎯 TARGET: Individual doctors and researchers across all medical sciences
    # We search specifically for personal emails in research contexts
    queries = [
        '"@gmail.com" medical research paper help India',
        '"@yahoo.com" clinical case report publication PhD',
        '"@outlook.com" manuscript editing services medical',
        'site:researchgate.net "gmail.com" medical author'
    ]
    
    # This logic forces the search to ignore 'info' results
    print("🛰️ Scouting Global Medical Authors (Gmail/Yahoo/Outlook)...")
    
    # ... your scraping logic here ...
    # Ensure it returns names/emails to the outreach_specialist
