import os
import requests
from dotenv import load_dotenv

# Load environment variables (for local dev)
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def call_llm(prompt: str):
    if not OPENROUTER_API_KEY:
        return "ERROR: API key missing"

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # ✅ Balanced system prompt
    system_prompt = (
    "You are a helpful AI assistant.\n"
    "The input may contain placeholder tokens such as [PERSON_1], [EMAIL_1], or [PHONE_1].\n"
    "\n"
    "Instructions:\n"
    "- Ignore placeholder format and focus on the meaning.\n"
    "- Do not mention or explain placeholders.\n"
    "- Do not show reasoning, thinking, or analysis.\n"
    "- Respond with only the final answer.\n"
    "- Follow the user’s format exactly (e.g., if asked for 2 lines, return exactly 2 lines).\n"
    )

    data = {
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,   # ✅ stable output
        "top_p": 1,
        "max_tokens": 150
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code != 200:
            return f"LLM ERROR: {response.text}"

        result = response.json()

        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"].strip()
        else:
            return f"LLM ERROR RESPONSE: {result}"

    except requests.exceptions.Timeout:
        return "LLM ERROR: Request timed out"

    except Exception as e:
        return f"EXCEPTION: {str(e)}"