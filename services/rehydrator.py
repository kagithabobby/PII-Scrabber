import re

SENSITIVE = {"AADHAAR", "PAN", "PIN", "PHONE"}
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


def safe_rehydrate(
    text: str,
    mapping: dict[str, str],
    *,
    restore_sensitive: bool = False,
) -> str:
    if not mapping:
        return text

    ordered_placeholders = sorted(mapping.keys(), key=len, reverse=True)
    placeholder_pattern = "|".join(re.escape(item) for item in ordered_placeholders)
    annotated_pattern = re.compile(
        rf"(?P<placeholder>{placeholder_pattern})"
        r"(?:\s*\((?P<semantic>[^)]+)\))?"
    )

    def replace_match(match: re.Match[str]) -> str:
        placeholder = match.group("placeholder")
        label = placeholder.split("_", 1)[0].replace("[", "")
        if label in SENSITIVE and not restore_sensitive:
            return SEMANTIC_MAP.get(label, "sensitive data")
        return mapping.get(placeholder, placeholder)

    return annotated_pattern.sub(replace_match, text)
