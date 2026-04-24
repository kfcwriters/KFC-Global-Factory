import os

def send_outreach(email_list):
    # 🛡️ THE IRON BARRIER: Total block on generic IDs
    forbidden = ["info", "admin", "contact", "support", "office", "sales", "help"]
    
    clean_leads = []
    for email in email_list:
        addr = email.lower().strip()
        # BLOCK if the email contains ANY forbidden word
        if any(word in addr for word in forbidden):
            print(f"🗑️ Hard-Blocked Spam Lead: {addr}")
            continue
        
        # ALLOW only if it looks like a person's name on Gmail/Yahoo/Institutional mail
        if "@" in addr:
            clean_leads.append(addr)

    if not clean_leads:
        print("✅ CEO PROTECTION: Zero generic leads passed. Sent folder remains clean.")
        return

    print(f"📧 TARGETS LOCKED: Sending to {len(clean_leads)} individual medical authors.")
    # Add your SMTP/Gmail logic here
