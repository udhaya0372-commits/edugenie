from gemini_client import generate_content


def answer_question(question: str) -> str:
    prompt = f"""Answer the following question accurately and directly.
Explain the reasoning when it helps the learner understand the answer.

Question: {question}"""
    return generate_content(prompt)
