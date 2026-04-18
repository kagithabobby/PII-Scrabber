# import json
# from datetime import datetime
# import uuid

# def log_request(original, masked, mapping):
#     log_data = {
#         "request_id": str(uuid.uuid4()),
#         "timestamp": datetime.now().isoformat(),
#         "original": original,
#         "masked": masked,
#         "pii_detected": mapping
#     }

#     with open("logs.txt", "a") as f:
#         f.write(json.dumps(log_data) + "\n")

# services/logger.py
import json
from datetime import datetime
import uuid

LOG_FILE = "logs.txt"

def log_request(original, masked, mapping):
    log_data = {
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "original": original,
        "masked": masked,
        "pii_detected": mapping
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_data) + "\n")


# 🔥 NEW FUNCTION
def get_logs():
    logs = []
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                logs.append(json.loads(line.strip()))
    except FileNotFoundError:
        return []

    return logs