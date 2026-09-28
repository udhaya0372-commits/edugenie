from gemini_client import generate_content


def generate_quiz(topic: str) -> str:
    prompt = f"""Create a five-question quiz about the following topic.
Each question must have four answer options, identify the correct answer, and briefly explain it.
Format the response in Markdown and do not include a total score.

Topic: {topic}"""
    return generate_content(prompt)
