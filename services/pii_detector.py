# import re

# def mask_pii_with_mapping(text):
#     mapping = {}
#     email_count = 1
#     phone_count = 1

#     email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
#     def replace_email(match):
#         nonlocal email_count
#         placeholder = f"[EMAIL_{email_count}]"
#         mapping[placeholder] = match.group()
#         email_count += 1
#         return placeholder

#     text = re.sub(email_pattern, replace_email, text)

#     phone_pattern = r'\b\d{10}\b'

#     def replace_phone(match):
#         nonlocal phone_count
#         placeholder = f"[PHONE_{phone_count}]"
#         mapping[placeholder] = match.group()
#         phone_count += 1
#         return placeholder

#     text = re.sub(phone_pattern, replace_phone, text)

#     return text, mapping

import re
import spacy

nlp = spacy.load("en_core_web_sm")

def mask_pii_with_mapping(text):
    mapping = {}

    email_count = 1
    phone_count = 1
    person_count = 1
    org_count = 1
    loc_count = 1
    aadhaar_count = 1
    pan_count = 1

    # ------------------------
    # EMAIL (Regex)
    # ------------------------
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

    def replace_email(match):
        nonlocal email_count
        placeholder = f"[EMAIL_{email_count}]"
        mapping[placeholder] = match.group()
        email_count += 1
        return placeholder

    text = re.sub(email_pattern, replace_email, text)

    # ------------------------
    # PHONE (Regex)
    # ------------------------
    phone_pattern = r'\b\d{10}\b'

    def replace_phone(match):
        nonlocal phone_count
        placeholder = f"[PHONE_{phone_count}]"
        mapping[placeholder] = match.group()
        phone_count += 1
        return placeholder

    text = re.sub(phone_pattern, replace_phone, text)

    # ------------------------
    # AADHAAR (Regex)
    # ------------------------
    aadhaar_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'

    def replace_aadhaar(match):
        nonlocal aadhaar_count
        placeholder = f"[AADHAAR_{aadhaar_count}]"
        mapping[placeholder] = match.group()
        aadhaar_count += 1
        return placeholder

    text = re.sub(aadhaar_pattern, replace_aadhaar, text)

    # ------------------------
    # PAN (Regex)
    # ------------------------
    pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'

    def replace_pan(match):
        nonlocal pan_count
        placeholder = f"[PAN_{pan_count}]"
        mapping[placeholder] = match.group()
        pan_count += 1
        return placeholder

    text = re.sub(pan_pattern, replace_pan, text)

    # ------------------------
    # NER (AI-based detection)
    # ------------------------
    doc = nlp(text)

    for ent in doc.ents:
        if ent.text in mapping.values():
            continue

        if ent.label_ == "PERSON":
            placeholder = f"[PERSON_{person_count}]"
            mapping[placeholder] = ent.text
            text = text.replace(ent.text, placeholder)
            person_count += 1

        elif ent.label_ == "ORG":
            placeholder = f"[ORG_{org_count}]"
            mapping[placeholder] = ent.text
            text = text.replace(ent.text, placeholder)
            org_count += 1

        elif ent.label_ in ["GPE", "LOC"]:
            placeholder = f"[LOC_{loc_count}]"
            mapping[placeholder] = ent.text
            text = text.replace(ent.text, placeholder)
            loc_count += 1

    return text, mapping