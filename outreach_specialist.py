import os

def send_outreach(email_list):
    # 🛡️ THE IRON GATE: List of words that trigger an immediate block
    trash_words = ["info", "admin", "office", "support", "contact", "sales", "help", "enquiry"]
    
    clean_list = []
    for email in email_list:
        addr = email.lower().strip()
        # Rule: If the part before the @ contains any trash words, DELETE IT.
        prefix = addr.split('@')[0]
        if any(word in prefix for word in trash_words):
            print(f"🗑️ Trash Lead Blocked: {addr}")
            continue
        
        clean_list.append(addr)

    if not clean_list:
        print("✅ CEO PROTECTION: No high-quality leads found this hour. Standing by.")
        return

    print(f"📧 TARGET ACQUIRED: Sending to {len(clean_list)} real clinical researchers.")
    # Add your SMTP/Gmail sending logic here
