from gemini_client import generate_content


def summarize_text(text: str) -> str:
    prompt = f"""Summarize the following text accurately and concisely.
Preserve the key ideas and use clear Markdown paragraphs or bullet points.

Text:
{text}"""
    return generate_content(prompt)
