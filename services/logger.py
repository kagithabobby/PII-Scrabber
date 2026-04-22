import json
import threading
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from services.pii_detector import get_active_spacy_model

LOG_FILE = Path(__file__).resolve().parent.parent / "logs.txt"
_LOG_LOCK = threading.Lock()


def log_request(
    original: str,
    masked: str,
    mapping: dict[str, str],
    detected_entities: list[dict],
    latency_ms: float,
) -> None:
    confidence_by_label: dict[str, list[float]] = defaultdict(list)
    for entity in detected_entities:
        confidence = entity.get("confidence")
        if isinstance(confidence, (int, float)):
            confidence_by_label[str(entity.get("label", "UNKNOWN"))].append(
                float(confidence)
            )

    log_data = {
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "original": original,
        "masked": masked,
        "pii_detected": mapping,
        "detected_entities": detected_entities,
        "latency_ms": round(latency_ms, 2),
        "spacy_model": get_active_spacy_model(),
        "confidence_summary": {
            label: round(sum(values) / len(values), 4)
            for label, values in confidence_by_label.items()
        },
    }

    with _LOG_LOCK:
        with LOG_FILE.open("a", encoding="utf-8") as file_handle:
            file_handle.write(json.dumps(log_data, ensure_ascii=False) + "\n")


def get_logs() -> list[dict]:
    if not LOG_FILE.exists():
        return []

    logs: list[dict] = []
    with _LOG_LOCK:
        with LOG_FILE.open("r", encoding="utf-8") as file_handle:
            for line in file_handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return logs


def get_log_summaries() -> list[dict]:
    summaries: list[dict] = []

    for log in get_logs():
        pii_detected = log.get("pii_detected", {})
        pii_types = sorted(
            {
                placeholder.split("_", 1)[0].replace("[", "")
                for placeholder in pii_detected.keys()
            }
        )
        summaries.append(
            {
                "request_id": log.get("request_id"),
                "timestamp": log.get("timestamp"),
                "pii_count": len(pii_detected),
                "pii_types": pii_types,
                "latency_ms": log.get("latency_ms"),
                "spacy_model": log.get("spacy_model"),
                "confidence_summary": log.get("confidence_summary"),
            }
        )

    return summaries
