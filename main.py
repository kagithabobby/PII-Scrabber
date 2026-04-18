# Phase 1

# from fastapi import FastAPI
# import re

# app = FastAPI()

# # ------------------------
# # PII Detection Functions
# # ------------------------

# def mask_email(text):
#     email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
#     return re.sub(email_pattern, '[EMAIL]', text)

# def mask_phone(text):
#     phone_pattern = r'\b\d{10}\b'
#     return re.sub(phone_pattern, '[PHONE]', text)

# def scrub_pii(text):
#     text = mask_email(text)
#     text = mask_phone(text)
#     return text

# # ------------------------
# # API Endpoint
# # ------------------------

# @app.post("/sanitize")
# def sanitize_text(data: dict):
#     input_text = data.get("text", "")
    
#     cleaned_text = scrub_pii(input_text)
    
#     return {
#         "original": input_text,
#         "sanitized": cleaned_text
#     }



# Phase 2

# from fastapi import FastAPI
# import re

# app = FastAPI()

# # ------------------------
# # PII Detection + Mapping
# # ------------------------

# def mask_pii_with_mapping(text):
#     mapping = {}
#     email_count = 1
#     phone_count = 1

#     # Email pattern
#     email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
#     def replace_email(match):
#         nonlocal email_count
#         placeholder = f"[EMAIL_{email_count}]"
#         mapping[placeholder] = match.group()
#         email_count += 1
#         return placeholder

#     text = re.sub(email_pattern, replace_email, text)

#     # Phone pattern
#     phone_pattern = r'\b\d{10}\b'

#     def replace_phone(match):
#         nonlocal phone_count
#         placeholder = f"[PHONE_{phone_count}]"
#         mapping[placeholder] = match.group()
#         phone_count += 1
#         return placeholder

#     text = re.sub(phone_pattern, replace_phone, text)

#     return text, mapping

# # ------------------------
# # API Endpoint
# # ------------------------

# @app.post("/sanitize")
# def sanitize_text(data: dict):
#     input_text = data.get("text", "")
    
#     masked_text, mapping = mask_pii_with_mapping(input_text)
    
#     return {
#         "original": input_text,
#         "sanitized": masked_text,
#         "mapping": mapping
#     }


# Phase 3


# from fastapi import FastAPI
# import re

# app = FastAPI()

# # ------------------------
# # PII Detection + Mapping
# # ------------------------

# def mask_pii_with_mapping(text):
#     mapping = {}
#     email_count = 1
#     phone_count = 1

#     email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
#     def replace_email(match):
#         nonlocal email_count
#         placeholder = f"[EMAIL_{email_count}]"
#         mapping[placeholder] = match.group()
#         email_count += 1
#         return placeholder

#     text = re.sub(email_pattern, replace_email, text)

#     phone_pattern = r'\b\d{10}\b'

#     def replace_phone(match):
#         nonlocal phone_count
#         placeholder = f"[PHONE_{phone_count}]"
#         mapping[placeholder] = match.group()
#         phone_count += 1
#         return placeholder

#     text = re.sub(phone_pattern, replace_phone, text)

#     return text, mapping

# # ------------------------
# # FAKE LLM (simulate AI)
# # ------------------------

# def fake_llm_response(text):
#     return f"AI Response: {text}"

# # ------------------------
# # REHYDRATION
# # ------------------------

# def rehydrate(text, mapping):
#     for placeholder, real_value in mapping.items():
#         text = text.replace(placeholder, real_value)
#     return text

# # ------------------------
# # API Endpoint
# # ------------------------

# @app.post("/chat")
# def chat(data: dict):
#     input_text = data.get("text", "")

#     # Step 1: Mask
#     masked_text, mapping = mask_pii_with_mapping(input_text)

#     # Step 2: Send to AI
#     llm_response = fake_llm_response(masked_text)

#     # Step 3: Rehydrate
#     final_response = rehydrate(llm_response, mapping)

#     return {
#         "original": input_text,
#         "masked": masked_text,
#         "llm_response": llm_response,
#         "final_response": final_response
#     }


#phase 4


# from fastapi import FastAPI
# import re
# import requests

# app = FastAPI()

# # ------------------------
# # CONFIG
# # ------------------------

# OPENROUTER_API_KEY = "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"

# ------------------------
# PII Detection + Mapping
# ------------------------

# def mask_pii_with_mapping(text):
#     mapping = {}
#     email_count = 1
#     phone_count = 1

#     email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
#     def replace_email(match):
#         nonlocal email_count
#         placeholder = f"[EMAIL_{email_count}]"
#         mapping[placeholder] = match.group()
#         email_count += 1
#         return placeholder

#     text = re.sub(email_pattern, replace_email, text)

#     phone_pattern = r'\b\d{10}\b'

#     def replace_phone(match):
#         nonlocal phone_count
#         placeholder = f"[PHONE_{phone_count}]"
#         mapping[placeholder] = match.group()
#         phone_count += 1
#         return placeholder

#     text = re.sub(phone_pattern, replace_phone, text)

#     return text, mapping

# # ------------------------
# # REAL LLM CALL
# # ------------------------

# def call_llm(prompt):
#     url = "https://openrouter.ai/api/v1/chat/completions"

#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         "Content-Type": "application/json"
#     }

#     data = {
#         "model": "nvidia/nemotron-3-super-120b-a12b:free",  # safer model
#         "messages": [
#             {"role": "user", "content": prompt}
#         ]
#     }

#     response = requests.post(url, headers=headers, json=data)

#     print("STATUS:", response.status_code)
#     print("RAW RESPONSE:", response.text)

#     try:
#         result = response.json()
#         return result["choices"][0]["message"]["content"]
#     except Exception as e:
#         return f"LLM Error: {response.text}"

# # ------------------------
# # REHYDRATION
# # ------------------------

# def rehydrate(text, mapping):
#     for placeholder, real_value in mapping.items():
#         text = text.replace(placeholder, real_value)
#     return text

# # ------------------------
# # API Endpoint
# # ------------------------

# @app.post("/chat")
# def chat(data: dict):
#     input_text = data.get("text", "")

#     # Step 1: Mask
#     masked_text, mapping = mask_pii_with_mapping(input_text)

#     # Step 2: Call real AI
#     llm_response = call_llm(masked_text)

#     # Step 3: Rehydrate
#     final_response = rehydrate(llm_response, mapping)

#     return {
#         "original": input_text,
#         "masked": masked_text,
#         "llm_response": llm_response,
#         "final_response": final_response
#     }



# Note: The above code is a combination of all the phases, with the real LLM call integrated. The PII detection, mapping, and rehydration functions are defined as before, but you can modularize them into separate files for better organization.

# from fastapi import FastAPI
# from services.logger import log_request
# from services.pii_detector import mask_pii_with_mapping
# from services.llm_service import call_llm
# from services.rehydrator import rehydrate

# app = FastAPI()

# @app.get("/")
# def home():
#     return {"message": "PII Scrubber API Running"}

# @app.post("/chat")
# def chat(data: dict):
#     input_text = data.get("text", "")

#     masked_text, mapping = mask_pii_with_mapping(input_text)
#     llm_response = call_llm(masked_text)
#     final_response = rehydrate(llm_response, mapping)

#     return {
#         "original": input_text,
#         "masked": masked_text,
#         "llm_response": llm_response,
#         "final_response": final_response
#     }


# updated main.py with modularized code and logging

from fastapi import FastAPI
from services.logger import log_request
from services.pii_detector import mask_pii_with_mapping
from services.llm_service import call_llm
from services.rehydrator import rehydrate

app = FastAPI()

@app.get("/")
def home():
    return {"message": "PII Scrubber API Running"}

@app.post("/chat")
def chat(data: dict):
    input_text = data.get("text", "")

    # Step 1: Mask PII
    masked_text, mapping = mask_pii_with_mapping(input_text)

    # ✅ ADD LOGGING HERE (IMPORTANT)
    log_request(input_text, masked_text, mapping)

    # Step 2: Call LLM
    llm_response = call_llm(masked_text)

    # Step 3: Rehydrate
    final_response = rehydrate(llm_response, mapping)

    return {
        "original": input_text,
        "masked": masked_text,
        "llm_response": llm_response,
        "final_response": final_response
    }