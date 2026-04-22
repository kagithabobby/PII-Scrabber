import logging
from pathlib import Path
from time import perf_counter

logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from services.llm_service import call_llm
from services.logger import get_log_summaries, log_request
from services.pii_detector import hybrid_mask
from services.rehydrator import safe_rehydrate

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="PII Scrabber API",
    version="1.0.0",
    description="Privacy-preserving middleware that masks PII before sending prompts to an LLM.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class ChatRequest(BaseModel):
    text: str = Field(default="", max_length=10000)


class DetectedEntity(BaseModel):
    label: str
    value: str
    placeholder: str
    semantic: str
    confidence: float
    source: str
    start: int
    end: int


class ChatResponse(BaseModel):
    original: str
    masked: str
    llm_response: str
    final_response: str
    detected_entities: list[DetectedEntity]
    latency_ms: float


class LogSummary(BaseModel):
    request_id: str | None = None
    timestamp: str | None = None
    pii_count: int
    pii_types: list[str]
    latency_ms: float | None = None
    spacy_model: str | None = None
    confidence_summary: dict[str, float] | None = None


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@app.get("/")
@app.get("/dashboard")
def dashboard() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "dashboard.html")


@app.get("/logs", response_model=list[LogSummary])
def list_logs() -> list[LogSummary]:
    return [LogSummary(**item) for item in get_log_summaries()]


@app.post("/chat", response_model=ChatResponse)
def chat(data: ChatRequest) -> ChatResponse:
    input_text = data.text.strip()
    if not input_text:
        raise HTTPException(status_code=400, detail="`text` must not be empty.")

    started_at = perf_counter()

    try:
        masked_text, mapping, detected_entities = hybrid_mask(input_text)
        llm_data = call_llm(masked_text)
        llm_response = llm_data['reply']
        final_response = safe_rehydrate(llm_response, mapping, restore_sensitive=True)
        if mapping and final_response == llm_response:
            logger.warning("Restoration skipped: No placeholders found in LLM response.")
            
        latency_ms = (perf_counter() - started_at) * 1000
        log_request(
            input_text,
            masked_text,
            mapping,
            detected_entities,
            latency_ms,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to process request.") from exc

    return ChatResponse(
        original=input_text,
        masked=masked_text,
        llm_response=llm_response,
        final_response=final_response,
        detected_entities=[DetectedEntity(**item) for item in detected_entities],
        latency_ms=round(latency_ms, 2),
    )
