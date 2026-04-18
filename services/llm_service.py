# import requests
# import os
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# def call_llm(prompt):
      
#     print("API KEY:", OPENROUTER_API_KEY)
#     print("STATUS:", response.status_code)
#     print("RESPONSE:", response.text)
#     # DEBUG
#     url = "https://openrouter.ai/api/v1/chat/completions"

#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         "Content-Type": "application/json"
#     }

#     data = {
#         "model": "nvidia/nemotron-3-super-120b-a12b:free",
#         "messages": [
#             {"role": "user", "content": prompt}
#         ]
#     }

#     response = requests.post(url, headers=headers, json=data)

#     try:
#         result = response.json()
#         return result["choices"][0]["message"]["content"]
#     except:
#         return f"LLM Error: {response.text}"
#     print("API KEY:", OPENROUTER_API_KEY)

import os

from flask.cli import load_dotenv


def call_llm(prompt):
    import requests
    # import os

    # OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    import os
    from dotenv import load_dotenv

    load_dotenv()

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    if not OPENROUTER_API_KEY:
        return "ERROR: API key missing in Render environment"

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        result = response.json()

        # ✅ SAFE CHECK
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return f"LLM ERROR RESPONSE: {result}"

    except Exception as e:
        return f"EXCEPTION: {str(e)}"