import re

def mask_pii_with_mapping(text):
    mapping = {}
    email_count = 1
    phone_count = 1

    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
    def replace_email(match):
        nonlocal email_count
        placeholder = f"[EMAIL_{email_count}]"
        mapping[placeholder] = match.group()
        email_count += 1
        return placeholder

    text = re.sub(email_pattern, replace_email, text)

    phone_pattern = r'\b\d{10}\b'

    def replace_phone(match):
        nonlocal phone_count
        placeholder = f"[PHONE_{phone_count}]"
        mapping[placeholder] = match.group()
        phone_count += 1
        return placeholder

    text = re.sub(phone_pattern, replace_phone, text)

    return text, mapping