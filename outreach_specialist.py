import os
import requests
import smtplib
import random
import re
from email.message import EmailMessage

def hunt_real_medical_leads():
    """
    Hunts real author emails from the PubMed (NCBI) database.
    This ensures we never 'guess' an email address again.
    """
    fields = ["Oncology", "Biochemistry", "Cardiology", "Surgery", "Diabetes", "Nephrology"]
    selected_field = random.choice(fields)
    print(f"🔭 PubMed Hunt: Searching for recent authors in {selected_field}...")

    # Step 1: Search PubMed for recent articles in the chosen field
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={selected_field}&retmax=5&retmode=json"
    try:
        search_resp = requests.get(search_url).json()
        ids = search_resp.get('esearchresult', {}).get('idlist', [])
        
        real_emails = []
        # Step 2: Fetch details for these specific papers to find author emails
        for pm_id in ids:
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pm_id}&retmode=xml"
            fetch_resp = requests.get(fetch_url).text
            
            # Use Regex to find email addresses in the XML metadata
            found_emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', fetch_resp)
            if found_emails:
                # Filter out generic publisher emails
                valid = [e for e in found_emails if "elsevier" not in e and "nature" not in e]
                real_emails.extend(valid)
        
        return selected_field, list(set(real_emails))[:5] # Return top 5 unique real leads
    except Exception as e:
        print(f"❌ Scraper Error: {e}")
        return selected_field, []

def run_outreach_strike():
    # 🔑 Credentials from GitHub Secrets
    tg_token = os.getenv('TELEGRAM_TOKEN')
    gmail_pass = os.getenv('GMAIL_PASSWORD')
    my_email = "kfcwriters@gmail.com"
    chat_id = "1060905337"

    # 🕵️ Get Real Leads
    field, leads = hunt_real_medical_leads()

    if not leads:
        print("⚠️ No real emails found this hour. Standing by.")
        return

    # 📧 Send the Elaborate PhD Pitch to Real People
    if gmail_pass:
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(my_email, gmail_pass)
                
                for email in leads:
                    msg = EmailMessage()
                    msg['Subject'] = f"PhD-Level Research & Publication Support: {field}"
                    msg['From'] = f"KFC Lab - Chief Research Specialist <{my_email}>"
                    msg['To'] = email
                    
                    body = (
                        "Dear Lead Researcher,\n\n"
                        "I am a Clinical Scientist and PhD Researcher providing end-to-end medical writing and publication support across the clinical spectrum.\n\n"
                        "Our team specializes in:\n"
                        "🧪 CLINICAL: Surgical Case Reports, Trials, and Meta-Analyses.\n"
                        "🎓 ACADEMIC: PhD Thesis drafting and MBBS Curriculum Design.\n"
                        "⚖️ REGULATORY: Pharma compliance and Biochemistry protocols.\n"
                        "📊 QUALITY: Six Sigma implementation in Laboratory Management.\n\n"
                        f"I noticed your recent contributions to the field of {field}. We are currently specializing in high-impact manuscript drafting and publication strategy in this niche.\n\n"
                        "I am available to assist you or your doctoral candidates in producing high-impact, peer-reviewed content.\n\n"
                        "Best Regards,\n"
                        "KFC Lab - Chief Research Specialist"
                    )
                    msg.set_content(body)
                    server.send_message(msg)
            
            # 📲 Report Success to Telegram
            report = f"🎯 PREDATOR STRIKE SUCCESS\nField: {field}\nLeads: {len(leads)} REAL researchers pitched."
            requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={"chat_id": chat_id, "text": report})
            print(f"✅ Success: {len(leads)} real leads hit.")
            
        except Exception as e:
            print(f"❌ Gmail Error: {e}")

if __name__ == "__main__":
    run_outreach_strike()
