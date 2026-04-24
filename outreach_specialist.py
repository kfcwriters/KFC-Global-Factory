import os

def send_outreach(email_list):
    # 🛡️ THE SMART BARRIER
    # Block generic roles, but ALLOW individual names on any provider.
    generic_roles = ["info", "admin", "office", "support", "contact", "sales", "help", "enquiry", "webmaster"]
    
    verified_authors = []
    for email in email_list:
        addr = email.lower().strip()
        prefix = addr.split('@')[0]
        
        # ❌ BLOCK if the prefix is JUST a generic word (like info@)
        # ✅ ALLOW if the prefix looks like a name (even on gmail/yahoo)
        if any(prefix == role for role in generic_roles):
            print(f"🗑️ Blocking generic role: {addr}")
            continue
        
        # Additional check: block things like info24@ or admin_test@
        if any(addr.startswith(role) for role in generic_roles):
             print(f"🗑️ Blocking suspected spam prefix: {addr}")
             continue

        verified_authors.append(addr)

    if not verified_authors:
        print("✅ CEO PROTECTION: Only generic roles found. Standing by.")
        return

    print(f"📧 TARGETS LOCKED: Sending PhD pitch to {len(verified_authors)} individual researchers (Personal & Institutional).")
    # ... Gmail/SMTP logic ...
