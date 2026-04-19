from fastapi import FastAPI
from services.pii_detector import hybrid_mask
from services.llm_service import call_llm
from services.rehydrator import safe_rehydrate
from services.logger import log_request

app = FastAPI()

@app.post("/chat")
def chat(data: dict):
    input_text = data.get("text", "")

    # Step 1: Hybrid Mask
    masked_text, mapping = hybrid_mask(input_text)

    # Step 2: LLM
    llm_data = call_llm(masked_text)

    # Step 3: Format Output
    if isinstance(llm_data, dict):
        llm_response = (
            f"Subject: {llm_data['subject']}\n\n"
            f"{llm_data['body']}\n\n"
            f"{llm_data['signature']}"
        )
    else:
        llm_response = llm_data

    # Step 4: Safe Rehydrate
    final_response = safe_rehydrate(llm_response, mapping)

    # Step 5: Log
    log_request(input_text, masked_text, mapping)

    return {
        "original": input_text,
        "masked": masked_text,
        "final_response": final_response
    }