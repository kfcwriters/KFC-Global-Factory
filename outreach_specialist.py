import os

def send_outreach(email_list):
    # 🛡️ THE ACADEMIC FILTER
    # Block generic roles, but ALLOW individual authors on personal domains
    generic_roles = ["info", "admin", "office", "support", "contact", "sales", "help", "webmaster", "enquiry"]
    
    verified_leads = []
    for email in email_list:
        addr = email.lower().strip()
        prefix = addr.split('@')[0]
        
        # 1. HARD BLOCK: If the prefix is exactly a generic word
        if any(prefix == role for role in generic_roles):
            print(f"🗑️ Blocking generic role: {addr}")
            continue
            
        # 2. PATTERN BLOCK: If it starts with 'info' followed by numbers
        if any(addr.startswith(role) for role in generic_roles):
            print(f"🗑️ Blocking suspected spam prefix: {addr}")
            continue

        # 3. VERIFIED: It looks like a real person's name
        verified_leads.append(addr)

    if not verified_leads:
        print("✅ CEO PROTECTION: Only generic roles found this hour. Skipping send.")
        return

    print(f"📧 TARGETS ACQUIRED: Sending PhD support pitch to {len(verified_leads)} authentic authors.")
    # Add your Gmail sending logic here...
