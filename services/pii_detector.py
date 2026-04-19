import re
import spacy

# Load once (important for performance)
nlp = spacy.load("en_core_web_sm")

# ------------------------
# REGEX PATTERNS
# ------------------------
EMAIL_RE = re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')
PHONE_RE = re.compile(r'\b\d{10}\b')
AADHAAR_RE = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
PAN_RE = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')
PIN_RE = re.compile(r'\b\d{4,6}\b')  # PIN / OTP-like

# ------------------------
# IGNORE WORDS
# ------------------------
IGNORE_WORDS = {"PAN", "EMAIL", "AADHAAR", "PIN", "OTP"}

# ------------------------
# PRIORITY (LOW = HIGH PRIORITY)
# ------------------------
PRIORITY = {
    "EMAIL": 1,
    "PHONE": 1,
    "AADHAAR": 1,
    "PAN": 1,
    "PIN": 1,
    "PERSON": 2,
    "ORG": 3,
    "LOC": 3
}

# ------------------------
# MAIN FUNCTION
# ------------------------
def mask_pii_with_mapping(text: str):
    if not text or not isinstance(text, str):
        return "", {}

    mapping = {}

    counts = {
        "EMAIL": 1,
        "PHONE": 1,
        "AADHAAR": 1,
        "PAN": 1,
        "PIN": 1,
        "PERSON": 1,
        "ORG": 1,
        "LOC": 1
    }

    spans = []

    # ------------------------
    # 1) REGEX DETECTION
    # ------------------------
    for m in EMAIL_RE.finditer(text):
        spans.append((m.start(), m.end(), "EMAIL", m.group()))

    for m in PHONE_RE.finditer(text):
        spans.append((m.start(), m.end(), "PHONE", m.group()))

    for m in AADHAAR_RE.finditer(text):
        spans.append((m.start(), m.end(), "AADHAAR", m.group()))

    for m in PAN_RE.finditer(text):
        spans.append((m.start(), m.end(), "PAN", m.group()))

    for m in PIN_RE.finditer(text):
        # Avoid masking already detected numbers
        val = m.group()
        if any(val == s[3] for s in spans):
            continue
        spans.append((m.start(), m.end(), "PIN", val))

    # ------------------------
    # 2) NER DETECTION
    # ------------------------
    doc = nlp(text)

    for ent in doc.ents:
        val = ent.text.strip()

        if not val or val.upper() in IGNORE_WORDS:
            continue

        if ent.label_ == "PERSON":
            spans.append((ent.start_char, ent.end_char, "PERSON", val))

        elif ent.label_ == "ORG":
            spans.append((ent.start_char, ent.end_char, "ORG", val))

        elif ent.label_ in ("GPE", "LOC"):
            spans.append((ent.start_char, ent.end_char, "LOC", val))

    # ------------------------
    # 3) RESOLVE OVERLAPS
    # ------------------------
    spans.sort(key=lambda x: (x[0], PRIORITY[x[2]], -(x[1] - x[0])))

    resolved = []
    occupied = [False] * len(text)
    seen_values = set()

    for s, e, label, val in spans:
        if val in seen_values:
            continue

        if any(occupied[i] for i in range(s, e)):
            continue

        for i in range(s, e):
            occupied[i] = True

        resolved.append((s, e, label, val))
        seen_values.add(val)

    # ------------------------
    # 4) REPLACE RIGHT → LEFT
    # ------------------------
    resolved.sort(key=lambda x: x[0], reverse=True)

    output = text

    for s, e, label, val in resolved:
        placeholder = f"[{label}_{counts[label]}]"
        counts[label] += 1

        mapping[placeholder] = val
        output = output[:s] + placeholder + output[e:]

    return output, mapping



# import re
# import spacy

# nlp = spacy.load("en_core_web_sm")

# # ------------------------
# # REGEX PATTERNS
# # ------------------------
# EMAIL_RE = re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')
# PHONE_RE = re.compile(r'\b\d{10}\b')
# AADHAAR_RE = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
# PAN_RE = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')
# PIN_RE = re.compile(r'\b\d{4,6}\b')

# # ------------------------
# # SEMANTIC REPLACEMENTS
# # ------------------------
# SEMANTIC_MAP = {
#     "EMAIL": "an email address",
#     "PHONE": "a phone number",
#     "AADHAAR": "an ID number",
#     "PAN": "a tax ID",
#     "PIN": "a PIN code",
#     "PERSON": "a person",
#     "ORG": "a company",
#     "LOC": "a location"
# }


# def semantic_mask(text: str):
#     if not text:
#         return ""

#     spans = []

#     # ---------- REGEX ----------
#     for m in EMAIL_RE.finditer(text):
#         spans.append((m.start(), m.end(), "EMAIL"))

#     for m in PHONE_RE.finditer(text):
#         spans.append((m.start(), m.end(), "PHONE"))

#     for m in AADHAAR_RE.finditer(text):
#         spans.append((m.start(), m.end(), "AADHAAR"))

#     for m in PAN_RE.finditer(text):
#         spans.append((m.start(), m.end(), "PAN"))

#     for m in PIN_RE.finditer(text):
#         spans.append((m.start(), m.end(), "PIN"))

#     # ---------- NER ----------
#     doc = nlp(text)

#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             spans.append((ent.start_char, ent.end_char, "PERSON"))

#         elif ent.label_ == "ORG":
#             spans.append((ent.start_char, ent.end_char, "ORG"))

#         elif ent.label_ in ("GPE", "LOC"):
#             spans.append((ent.start_char, ent.end_char, "LOC"))

#     # ---------- RESOLVE OVERLAPS ----------
#     spans.sort(key=lambda x: x[0])
#     resolved = []
#     occupied = [False] * len(text)

#     for s, e, label in spans:
#         if any(occupied[i] for i in range(s, e)):
#             continue

#         for i in range(s, e):
#             occupied[i] = True

#         resolved.append((s, e, label))

#     # ---------- REPLACE ----------
#     resolved.sort(key=lambda x: x[0], reverse=True)

#     output = text

#     for s, e, label in resolved:
#         replacement = SEMANTIC_MAP[label]
#         output = output[:s] + replacement + output[e:]

#     return output