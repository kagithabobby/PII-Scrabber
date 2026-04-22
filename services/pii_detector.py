import os
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import phonenumbers
import spacy

EMAIL_RE = re.compile(
    r"[\w\.+-]+@[\w-]+\.[\w\.-]+",
    re.IGNORECASE,
)
AADHAAR_RE = re.compile(r"(?<!\d)\d{4}\s?\d{4}\s?\d{4}(?!\d)")
PAN_RE = re.compile(r"(?<![A-Z0-9])[A-Z]{5}[0-9]{4}[A-Z](?![A-Z0-9])")
PIN_RE = re.compile(r"(?<!\d)\d{6}(?!\d)")

SEMANTIC_MAP = {
    "PERSON": "a person",
    "ORG": "a company",
    "LOC": "a location",
    "EMAIL": "an email",
    "PHONE": "a phone number",
    "AADHAAR": "an ID number",
    "PAN": "a tax ID",
    "PIN": "a PIN code",
}

@dataclass(frozen=True)
class Span:
    start: int
    end: int
    label: str
    value: str
    priority: int
    confidence: float
    source: str


@lru_cache(maxsize=1)
def get_nlp():
    model_name = os.getenv("SPACY_MODEL", "en_core_web_trf")
    fallback_model = os.getenv("SPACY_FALLBACK_MODEL", "en_core_web_sm")

    try:
        return spacy.load(model_name)
    except OSError:
        try:
            return spacy.load(fallback_model)
        except OSError:
            # Fall back to a blank pipeline so the API can still start without the model.
            return spacy.blank("en")


def get_active_spacy_model() -> str:
    return get_nlp().meta.get("name", "blank_en")





def _regex_spans(text: str) -> list[Span]:
    spans: list[Span] = []

    for match in EMAIL_RE.finditer(text):
        spans.append(
            Span(
                start=match.start(),
                end=match.end(),
                label="EMAIL",
                value=match.group(),
                priority=0,
                confidence=0.99,
                source="regex",
            )
        )

    for match in phonenumbers.PhoneNumberMatcher(text, "IN"):
        spans.append(
            Span(
                start=match.start,
                end=match.end,
                label="PHONE",
                value=match.raw_string,
                priority=0,
                confidence=0.99,
                source="phonenumbers",
            )
        )

    for regex, label in ((AADHAAR_RE, "AADHAAR"), (PAN_RE, "PAN"), (PIN_RE, "PIN")):
        for match in regex.finditer(text):
            spans.append(
                Span(
                    start=match.start(),
                    end=match.end(),
                    label=label,
                    value=match.group(),
                    priority=0,
                    confidence=0.99,
                    source="regex",
                )
            )

    return spans


def _spacy_confidence(ent: Any) -> float:
    confidence = ent.doc.user_data.get("entity_confidence", {}).get(
        (ent.start_char, ent.end_char, ent.label_)
    )
    if confidence is None:
        return 0.85
    try:
        return max(0.0, min(float(confidence), 1.0))
    except (TypeError, ValueError):
        return 0.85


def _collect_spans(text: str) -> list[Span]:
    spans = _regex_spans(text)

    doc = get_nlp()(text)
    for ent in doc.ents:
        label = None
        if ent.label_ == "PERSON":
            label = "PERSON"
        elif ent.label_ == "ORG":
            label = "ORG"
        elif ent.label_ in {"GPE", "LOC"}:
            label = "LOC"

        if label:
            spans.append(
                Span(
                    start=ent.start_char,
                    end=ent.end_char,
                    label=label,
                    value=ent.text,
                    priority=1,
                    confidence=_spacy_confidence(ent),
                    source="spacy",
                )
            )

    return spans


def _resolve_overlaps(spans: list[Span]) -> list[Span]:
    resolved: list[Span] = []

    for span in sorted(
        spans,
        key=lambda item: (item.start, item.priority, -(item.end - item.start)),
    ):
        has_overlap = any(
            not (span.end <= existing.start or span.start >= existing.end)
            for existing in resolved
        )
        if not has_overlap:
            resolved.append(span)

    return sorted(resolved, key=lambda item: item.start)


def hybrid_mask(text: str) -> tuple[str, dict[str, str], list[dict[str, Any]]]:
    mapping: dict[str, str] = {}
    detected_entities: list[dict[str, Any]] = []
    counts = {key: 1 for key in SEMANTIC_MAP}
    value_to_placeholder: dict[tuple[str, str], str] = {}

    spans = _resolve_overlaps(_collect_spans(text))
    if not spans:
        return text, mapping, detected_entities

    chunks: list[str] = []
    cursor = 0

    for span in spans:
        chunks.append(text[cursor:span.start])
        
        entity_key = (span.label, span.value)
        if entity_key in value_to_placeholder:
            placeholder = value_to_placeholder[entity_key]
        else:
            placeholder = f"[{span.label}_{counts[span.label]}]"
            counts[span.label] += 1
            value_to_placeholder[entity_key] = placeholder
            mapping[placeholder] = span.value
            
        detected_entities.append(
            {
                "label": span.label,
                "value": span.value,
                "placeholder": placeholder,
                "semantic": SEMANTIC_MAP[span.label],
                "confidence": round(span.confidence, 4),
                "source": span.source,
                "start": span.start,
                "end": span.end,
            }
        )
        chunks.append(f"{placeholder} ({SEMANTIC_MAP[span.label]})")
        cursor = span.end

    chunks.append(text[cursor:])
    return "".join(chunks), mapping, detected_entities
