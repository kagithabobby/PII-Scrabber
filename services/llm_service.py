import json
import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = os.getenv(
    "OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions"
)
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free"
)
REQUEST_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "15"))
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "300"))

SESSION = requests.Session()


def call_llm(prompt: str) -> dict[str, str]:
    if not OPENROUTER_API_KEY:
        return fallback_response()

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        "You are a helpful assistant. You will receive text where sensitive information "
        "has been replaced with placeholders like [PERSON_1] or [PHONE_1]. "
        "You MUST maintain these placeholders in your response so the system can restore them. "
        "Do not provide generic templates; respond directly to the user's request using the placeholders provided. "
        "Return ONLY valid JSON with a single string key `reply` containing your full conversational response."
    )

    user_content = (
        f"Please process the following request and respond using the required JSON format. "
        f"Remember to KEEP all placeholders exactly as they appear:\n\n"
        f"<user_input>\n{prompt}\n</user_input>"
    )

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0,
        "top_p": 1,
        "max_tokens": MAX_TOKENS,
    }

    try:
        response = SESSION.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        result = response.json()
        raw_output = (
            result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        parsed = parse_llm_json(raw_output)
        return parsed or fallback_response()
    except (requests.RequestException, ValueError, KeyError, IndexError) as e:
        print(f"Exception in call_llm: {e}")
        return fallback_response()


def parse_llm_json(text: str) -> dict[str, str] | None:
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if len(lines) >= 3:
            candidate = "\n".join(lines[1:-1]).strip()

    start_idx = candidate.find("{")
    end_idx = candidate.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        candidate = candidate[start_idx:end_idx+1]

    try:
        data: Any = json.loads(candidate)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}. Candidate was: {candidate}")
        return None

    required_keys = ("reply",)
    if not isinstance(data, dict) or any(key not in data for key in required_keys):
        return None

    normalized = {key: str(data[key]).strip() for key in required_keys}
    if not all(normalized.values()):
        return None

    return normalized


def fallback_response() -> dict[str, str]:
    return {
        "reply": (
            "Hello, I understand you need assistance with your request. "
            "Please review it and let me know the next steps."
        )
    }
