import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def call_llm(prompt: str):
    if not OPENROUTER_API_KEY:
        return fallback_response()

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are a professional assistant.\n"
        "Return ONLY valid JSON with keys: subject, body, signature.\n"
        "No explanation. No extra text."
    )

    data = {
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "top_p": 1,
        "max_tokens": 200
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code != 200:
            return fallback_response()

        result = response.json()

        if "choices" not in result:
            return fallback_response()

        raw_output = result["choices"][0]["message"]["content"].strip()

        parsed = parse_llm_json(raw_output)

        if not parsed:
            return fallback_response()

        return parsed

    except Exception:
        return fallback_response()


# ------------------------
# JSON PARSER
# ------------------------
def parse_llm_json(text: str):
    try:
        data = json.loads(text)

        if not all(k in data for k in ["subject", "body", "signature"]):
            return None

        return data

    except Exception:
        return None


# ------------------------
# FALLBACK RESPONSE
# ------------------------
def fallback_response():
    return {
        "subject": "Request for Aadhaar Update",
        "body": (
            "Dear Sir/Madam,\n\n"
            "I would like to request an update to my Aadhaar details. "
            "Kindly guide me on the required process and documents.\n\n"
            "Thank you."
        ),
        "signature": "Sincerely,\nA User"
    }