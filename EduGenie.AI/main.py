import logging
from pathlib import Path
from typing import Callable, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from config import get_settings
from explanation_module import explain_topic
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text


settings = get_settings()

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = TEMPLATES_DIR / "static"

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="EduGenie - Google Gemini powered learning assistant",
)

allowed_origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
logger = logging.getLogger(__name__)


class TextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=settings.max_input_chars,
        description="Educational text or question",
    )


def clean_input(value: str) -> str:
    if not isinstance(value, str):
        raise HTTPException(
            status_code=400,
            detail="Input must be text.",
        )

    value = value.strip()

    if not value:
        raise HTTPException(
            status_code=400,
            detail="Input cannot be empty.",
        )

    if len(value) > settings.max_input_chars:
        raise HTTPException(
            status_code=413,
            detail=(
                f"Input exceeds the maximum allowed length of "
                f"{settings.max_input_chars} characters."
            ),
        )

    return value


def run_ai_function(function: Callable[[str], Any], value: str) -> Any:
    cleaned_value = clean_input(value)

    try:
        return function(cleaned_value)
    except HTTPException:
        raise
    except Exception as exc:
        print(f"AI processing failed: {exc}")
        raise HTTPException(
            status_code=500,
            detail=f"AI ERROR: {repr(exc)}",
        ) from exc


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    index_file = TEMPLATES_DIR / "index.html"

    if not index_file.exists():
        return HTMLResponse(
            content=(
                "<h1>EduGenie</h1>"
                "<p>templates/index.html was not found.</p>"
            ),
            status_code=500,
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
            "ai_ready": bool(settings.gemini_api_key),
            "max_input_chars": settings.max_input_chars,
        },
    )


@app.get("/health")
async def health():
    ai_ready = bool(settings.gemini_api_key)
    return {
        "status": "ok" if ai_ready else "degraded",
        "app": settings.app_name,
        "environment": settings.app_env,
        "ai": "ready" if ai_ready else "missing_api_key",
    }


@app.post("/qa")
async def qa(request: TextRequest):
    return {
        "answer": await run_in_threadpool(
            run_ai_function,
            answer_question,
            request.text,
        ),
    }


@app.post("/explain")
async def explain(request: TextRequest):
    return {
        "explanation": await run_in_threadpool(
            run_ai_function,
            explain_topic,
            request.text,
        ),
    }


@app.post("/quiz")
async def quiz(request: TextRequest):
    return {
        "quiz": await run_in_threadpool(
            run_ai_function,
            generate_quiz,
            request.text,
        ),
    }


@app.post("/summarize")
async def summarize(request: TextRequest):
    return {
        "summary": await run_in_threadpool(
            run_ai_function,
            summarize_text,
            request.text,
        ),
    }


@app.post("/learn/recommendations")
async def recommendations(request: TextRequest):
    return {
        "recommendations": await run_in_threadpool(
            run_ai_function,
            get_learning_recommendations,
            request.text,
        ),
    }

