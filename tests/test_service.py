from services.llm_service import parse_llm_json
from services.pii_detector import hybrid_mask
from services.rehydrator import safe_rehydrate


def test_hybrid_mask_masks_detected_values_without_overlapping_corruption():
    text = "John lives in Delhi. Contact john@example.com or 9876543210."
    masked, mapping, detected_entities = hybrid_mask(text)

    assert "john@example.com" not in masked
    assert "9876543210" not in masked
    assert "[EMAIL_1]" in masked
    assert "[PHONE_1]" in masked
    assert mapping["[EMAIL_1]"] == "john@example.com"
    assert mapping["[PHONE_1]"].replace(" ", "").replace("-", "").endswith("9876543210")
    assert any(entity["label"] == "EMAIL" for entity in detected_entities)
    assert any(entity["label"] == "PHONE" for entity in detected_entities)
    assert all("confidence" in entity for entity in detected_entities)


def test_hybrid_mask_assigns_unique_placeholders_to_multiple_entities_of_same_type():
    text = "Reach Alice at alice@example.com and Bob at bob@example.com."
    masked, mapping, detected_entities = hybrid_mask(text)

    assert "[EMAIL_1]" in masked
    assert "[EMAIL_2]" in masked
    assert mapping["[EMAIL_1]"] == "alice@example.com"
    assert mapping["[EMAIL_2]"] == "bob@example.com"
    assert [entity["placeholder"] for entity in detected_entities if entity["label"] == "EMAIL"] == [
        "[EMAIL_1]",
        "[EMAIL_2]",
    ]


def test_hybrid_mask_detects_international_phone_formats_without_catching_random_ids():
    text = (
        "Call me on +91 98765 43210 or +1 (415) 555-2671. "
        "Ignore order number 12345678901234567890."
    )
    masked, mapping, _ = hybrid_mask(text)

    assert "[PHONE_1]" in masked
    assert "[PHONE_2]" in masked
    assert all(value != "12345678901234567890" for value in mapping.values())


def test_safe_rehydrate_restores_non_sensitive_values_and_keeps_sensitive_redacted():
    mapping = {
        "[PERSON_1]": "John",
        "[EMAIL_1]": "john@example.com",
        "[PHONE_1]": "9876543210",
    }
    text = (
        "Email john [EMAIL_1] and call [PHONE_1] (a phone number). "
        "[PERSON_1] (a person) raised the ticket."
    )

    rehydrated = safe_rehydrate(text, mapping)

    assert "john@example.com" in rehydrated
    assert "John" in rehydrated
    assert "9876543210" not in rehydrated
    assert "a phone number" in rehydrated


def test_safe_rehydrate_can_restore_sensitive_values_for_full_round_trip():
    mapping = {
        "[PHONE_1]": "+91 98765 43210",
        "[PAN_1]": "ABCDE1234F",
    }
    text = "Please call [PHONE_1] (a phone number) and verify [PAN_1] (a tax ID)."

    rehydrated = safe_rehydrate(text, mapping, restore_sensitive=True)

    assert "+91 98765 43210" in rehydrated
    assert "ABCDE1234F" in rehydrated


def test_safe_rehydrate_does_not_break_on_overlapping_placeholder_names():
    mapping = {
        "[PERSON_1]": "Alice",
        "[PERSON_10]": "Bob",
    }
    text = "[PERSON_10] (a person) escalated the issue to [PERSON_1]."

    rehydrated = safe_rehydrate(text, mapping)

    assert rehydrated == "Bob escalated the issue to Alice."


def test_parse_llm_json_supports_code_fences():
    parsed = parse_llm_json(
        "```json\n"
        '{"subject":"Hello","body":"World","signature":"Regards"}\n'
        "```"
    )

    assert parsed == {
        "subject": "Hello",
        "body": "World",
        "signature": "Regards",
    }
