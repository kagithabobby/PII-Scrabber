import json
from datetime import datetime
import uuid

def log_request(original, masked, mapping):
    log_data = {
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "original": original,
        "masked": masked,
        "pii_detected": mapping
    }

    with open("logs.txt", "a") as f:
        f.write(json.dumps(log_data) + "\n")