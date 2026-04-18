import re
import spacy

nlp = spacy.load("en_core_web_sm")

EMAIL_RE = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_RE = re.compile(r'\b\d{10}\b')
AADHAAR_RE = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
PAN_RE = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')

# simple stopwords to avoid over-detection
STOPWORDS = {"The", "This", "My", "Hello", "Hi", "Say", "Please"}

def mask_pii_with_mapping(text: str):
    mapping = {}

    counts = {
        "EMAIL": 1, "PHONE": 1, "AADHAAR": 1, "PAN": 1,
        "PERSON": 1, "ORG": 1, "LOC": 1
    }

    spans = []  # (start, end, label, value)

    # ---------- 1) Regex spans ----------
    for m in EMAIL_RE.finditer(text):
        spans.append((m.start(), m.end(), "EMAIL", m.group()))
    for m in PHONE_RE.finditer(text):
        spans.append((m.start(), m.end(), "PHONE", m.group()))
    for m in AADHAAR_RE.finditer(text):
        spans.append((m.start(), m.end(), "AADHAAR", m.group()))
    for m in PAN_RE.finditer(text):
        spans.append((m.start(), m.end(), "PAN", m.group()))

    # ---------- 2) NER spans ----------
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            spans.append((ent.start_char, ent.end_char, "PERSON", ent.text))
        elif ent.label_ == "ORG":
            spans.append((ent.start_char, ent.end_char, "ORG", ent.text))
        elif ent.label_ in ("GPE", "LOC"):
            spans.append((ent.start_char, ent.end_char, "LOC", ent.text))

    # ---------- 3) Heuristic PERSON (fallback) ----------
    # only if NER didn’t catch it; avoid stopwords
    words = list(re.finditer(r'\b[A-Z][a-z]+\b', text))
    for w in words:
        word = w.group()
        if word in STOPWORDS:
            continue
        # skip if already covered by a span
        if any(not (w.end() <= s or w.start() >= e) for (s, e, *_ ) in spans):
            continue
        spans.append((w.start(), w.end(), "PERSON", word))

    # ---------- 4) De-duplicate / resolve overlaps ----------
    # Prefer longer spans; then earlier ones
    spans.sort(key=lambda x: (x[0], -(x[1]-x[0])))
    resolved = []
    occupied = [False] * (len(text) + 1)

    for s, e, label, val in spans:
        if any(occupied[i] for i in range(s, e)):
            continue
        for i in range(s, e):
            occupied[i] = True
        resolved.append((s, e, label, val))

    # ---------- 5) Replace right-to-left ----------
    resolved.sort(key=lambda x: x[0], reverse=True)

    out = text
    for s, e, label, val in resolved:
        placeholder = f"[{label}_{counts[label]}]"
        counts[label] += 1
        mapping[placeholder] = val
        out = out[:s] + placeholder + out[e:]

    return out, mapping