import os

def send_outreach(email_list):
    # CEO RULE: Strictly block generic 'info' and 'admin' accounts
    blacklist = ["info", "admin", "office", "contact", "support", "sales", "help", "mail"]
    
    verified_leads = []
    for email in email_list:
        prefix = email.split('@')[0].lower()
        
        # Check if the email starts with any blacklisted word
        if any(prefix.startswith(word) for word in blacklist):
            print(f"🛡️ Filtering out generic lead: {email}")
            continue
            
        # Only allow professional looking emails
        if "@" in email and "." in email.split("@")[1]:
            verified_leads.append(email)

    if not verified_leads:
        print("✅ Filter Success: No generic 'info' emails found. Skipping send to protect reputation.")
        return

    # Only send to the high-quality leads remaining
    print(f"📧 Sending PhD pitch to {len(verified_leads)} high-quality clinical leads...")
    # ... rest of your send logic here
