import re
import spacy

nlp = spacy.load("en_core_web_sm")

# ------------------------
# REGEX PATTERNS
# ------------------------
EMAIL_RE = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_RE = re.compile(r'\b\d{10}\b')
AADHAAR_RE = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
PAN_RE = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')

# ------------------------
# FILTER WORDS
# ------------------------
STOPWORDS = {"The", "This", "My", "Hello", "Hi", "Say", "Please"}
IGNORE_WORDS = {"PAN", "EMAIL", "AADHAAR"}

# ------------------------
# PRIORITY
# ------------------------
PRIORITY = {
    "EMAIL": 1,
    "PHONE": 1,
    "AADHAAR": 1,
    "PAN": 1,
    "PERSON": 2,
    "ORG": 2,
    "LOC": 2
}

# ------------------------
# MAIN FUNCTION
# ------------------------
def mask_pii_with_mapping(text: str):
    mapping = {}

    counts = {
        "EMAIL": 1,
        "PHONE": 1,
        "AADHAAR": 1,
        "PAN": 1,
        "PERSON": 1,
        "ORG": 1,
        "LOC": 1
    }

    spans = []  # (start, end, label, value)

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

    # ------------------------
    # 2) NER DETECTION
    # ------------------------
    doc = nlp(text)

    for ent in doc.ents:
        val = ent.text.strip()

        # 🚫 skip keywords like PAN, EMAIL
        if val.upper() in IGNORE_WORDS:
            continue

        if ent.label_ == "PERSON":
            spans.append((ent.start_char, ent.end_char, "PERSON", val))

        elif ent.label_ == "ORG":
            spans.append((ent.start_char, ent.end_char, "ORG", val))

        elif ent.label_ in ("GPE", "LOC"):
            spans.append((ent.start_char, ent.end_char, "LOC", val))

    # ------------------------
    # 3) HEURISTIC PERSON (fallback)
    # ------------------------
    words = list(re.finditer(r'\b[A-Z][a-z]+\b', text))

    for w in words:
        word = w.group()

        if word in STOPWORDS or word.upper() in IGNORE_WORDS:
            continue

        # skip if already covered by another span
        if any(not (w.end() <= s or w.start() >= e) for (s, e, *_ ) in spans):
            continue

        spans.append((w.start(), w.end(), "PERSON", word))

    # ------------------------
    # 4) RESOLVE OVERLAPS
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
    # 5) REPLACE RIGHT → LEFT
    # ------------------------
    resolved.sort(key=lambda x: x[0], reverse=True)

    output = text

    for s, e, label, val in resolved:
        placeholder = f"[{label}_{counts[label]}]"
        counts[label] += 1

        mapping[placeholder] = val
        output = output[:s] + placeholder + output[e:]

    return output, mapping