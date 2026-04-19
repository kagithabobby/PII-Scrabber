import re
import spacy

nlp = spacy.load("en_core_web_sm")

EMAIL_RE = re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')
PHONE_RE = re.compile(r'\b\d{10}\b')
AADHAAR_RE = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
PAN_RE = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')
PIN_RE = re.compile(r'\b\d{4,6}\b')

SEMANTIC_MAP = {
    "PERSON": "a person",
    "ORG": "a company",
    "LOC": "a location",
    "EMAIL": "an email",
    "PHONE": "a phone number",
    "AADHAAR": "an ID number",
    "PAN": "a tax ID",
    "PIN": "a PIN"
}

def hybrid_mask(text):
    mapping = {}
    counts = {k:1 for k in SEMANTIC_MAP}

    spans = []

    # -------- REGEX --------
    patterns = [
        (EMAIL_RE, "EMAIL"),
        (PHONE_RE, "PHONE"),
        (AADHAAR_RE, "AADHAAR"),
        (PAN_RE, "PAN"),
        (PIN_RE, "PIN")
    ]

    for regex, label in patterns:
        for m in regex.finditer(text):
            spans.append((m.start(), m.end(), label, m.group()))

    # -------- NER --------
    doc = nlp(text)
    for ent in doc.ents:
        label = None
        if ent.label_ == "PERSON":
            label = "PERSON"
        elif ent.label_ == "ORG":
            label = "ORG"
        elif ent.label_ in ("GPE", "LOC"):
            label = "LOC"

        if label:
            spans.append((ent.start_char, ent.end_char, label, ent.text))

    # -------- REPLACE --------
    spans.sort(key=lambda x: x[0], reverse=True)

    output = text

    for s, e, label, val in spans:
        placeholder = f"[{label}_{counts[label]}]"
        counts[label] += 1

        mapping[placeholder] = val

        semantic = SEMANTIC_MAP[label]

        replacement = f"{placeholder} ({semantic})"

        output = output[:s] + replacement + output[e:]

    return output, mapping