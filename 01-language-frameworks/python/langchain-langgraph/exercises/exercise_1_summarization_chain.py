"""
Exercise 1: Build a Summarization Chain

Create a chain that takes long text and produces a structured summary.

Requirements:
1. Create a chain that summarizes text in 3 bullet points
2. The chain should also extract the main topic
3. Use structured output (Pydantic model) for the response
4. Handle text that is too short gracefully

Expected output format:
{
    "main_topic": "The primary subject of the text",
    "bullet_points": [
        "First key point",
        "Second key point",
        "Third key point"
    ],
    "word_count": 150
}

Hints:
- Use ChatPromptTemplate for the prompt
- Create a Pydantic model for the output structure
- Use model.with_structured_output() for reliable parsing
- Consider adding a validation step for minimum text length
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


# TODO: Define the output schema
class SummaryOutput(BaseModel):
    """Schema for the summary output."""
    # Add fields here:
    # - main_topic: str
    # - bullet_points: list[str] with exactly 3 items
    # - word_count: int
    pass


def create_summarization_chain():
    """Create a chain that summarizes text into structured output.

    Returns:
        A chain that takes {"text": "..."} and returns SummaryOutput
    """
    # TODO: Implement the chain
    # 1. Create a ChatPromptTemplate that asks for a summary
    # 2. Initialize ChatOpenAI model
    # 3. Use with_structured_output(SummaryOutput)
    # 4. Compose with pipe operator
    pass


def summarize_text(text: str) -> dict:
    """Summarize the given text.

    Args:
        text: The text to summarize

    Returns:
        Dictionary with main_topic, bullet_points, and word_count
    """
    # TODO: Implement
    # 1. Validate text length (minimum 50 words)
    # 2. Create and invoke the chain
    # 3. Return the result as a dict
    pass


# Test your implementation
if __name__ == "__main__":
    test_text = """
    Machine learning is a subset of artificial intelligence that enables systems
    to learn and improve from experience without being explicitly programmed.
    It focuses on developing computer programs that can access data and use it
    to learn for themselves. The process begins with observations or data, such
    as examples, direct experience, or instruction, to look for patterns in data
    and make better decisions in the future. The primary aim is to allow computers
    to learn automatically without human intervention and adjust actions accordingly.
    Machine learning algorithms are often categorized as supervised or unsupervised.
    Supervised learning uses labeled data to train models, while unsupervised
    learning finds patterns in unlabeled data.
    """

    print("Testing summarization chain...")
    result = summarize_text(test_text)

    if result:
        print(f"\nMain Topic: {result.get('main_topic')}")
        print(f"\nBullet Points:")
        for i, point in enumerate(result.get('bullet_points', []), 1):
            print(f"  {i}. {point}")
        print(f"\nWord Count: {result.get('word_count')}")
    else:
        print("Chain not implemented yet.")
