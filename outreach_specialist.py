import os

def send_outreach(email_list):
    # CEO HARD RULE: No generic info or admin emails allowed.
    final_leads = []
    forbidden = ["info", "admin", "office", "support", "contact", "sales"]
    
    for email in email_list:
        clean_email = email.lower().strip()
        # Rule 1: Must not contain forbidden words
        if any(word in clean_email for word in forbidden):
            print(f"🛡️ Blocking generic email: {clean_email}")
            continue
        # Rule 2: Must be a professional domain
        if "@" in clean_email and "." in clean_email:
            final_leads.append(clean_email)

    if not final_leads:
        print("✅ Filter Success: 0 generic emails passed. Factory safe.")
        return

    print(f"📧 Sending PhD pitch to {len(final_leads)} high-quality clinical leads.")
    # Proceed with your Gmail sending logic here...
