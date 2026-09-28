from gemini_client import generate_content


def explain_topic(topic: str) -> str:
    prompt = f"""Explain the following topic to a beginner in clear, accurate language.
Use a short introduction, break difficult ideas into simple steps, and include one practical example.

Topic: {topic}"""
    return generate_content(prompt)
