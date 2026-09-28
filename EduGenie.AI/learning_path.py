from gemini_client import generate_content


def get_learning_recommendations(topic: str) -> str:
    prompt = f"""Create a practical learning path for the following topic.
Include prerequisites, a numbered sequence of learning goals, suggested resources and exercises,
and a realistic way to measure progress.

Topic: {topic}"""
    return generate_content(prompt)
