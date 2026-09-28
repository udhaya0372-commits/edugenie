from functools import lru_cache
from typing import Any

from config import get_settings


@lru_cache
def _get_client() -> Any:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    from google import genai

    return genai.Client(api_key=settings.gemini_api_key)


def generate_content(prompt: str) -> str:
    settings = get_settings()
    interaction = _get_client().interactions.create(
        model=settings.gemini_model,
        input=prompt,
    )
    content = (interaction.output_text or "").strip()
    if not content:
        raise RuntimeError("Gemini returned an empty response")
    return content
