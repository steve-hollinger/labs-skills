"""
Solution 1: Summarization Chain

This solution demonstrates how to create a structured summarization chain
using LangChain with Pydantic output schemas.
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()


class SummaryOutput(BaseModel):
    """Schema for the summary output."""
    main_topic: str = Field(description="The primary subject or theme of the text")
    bullet_points: list[str] = Field(
        description="Exactly 3 key points from the text",
        min_length=3,
        max_length=3
    )
    word_count: int = Field(description="Number of words in the original text")


def create_summarization_chain():
    """Create a chain that summarizes text into structured output.

    Returns:
        A chain that takes {"text": "..."} and returns SummaryOutput
    """
    if not os.getenv("OPENAI_API_KEY"):
        # Return mock chain for demonstration
        return create_mock_chain()

    from langchain_openai import ChatOpenAI

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a text summarization expert. Your task is to:
1. Identify the main topic of the text
2. Extract exactly 3 key bullet points
3. Be concise but informative

Always respond with a structured summary."""),
        ("user", """Please summarize the following text:

{text}

Provide:
- The main topic (one phrase)
- Exactly 3 bullet points capturing the key information
- The word count is: {word_count}""")
    ])

    # Initialize model with structured output
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    structured_model = model.with_structured_output(SummaryOutput)

    # Create the chain
    def add_word_count(input_dict: dict) -> dict:
        text = input_dict.get("text", "")
        word_count = len(text.split())
        return {"text": text, "word_count": word_count}

    chain = RunnableLambda(add_word_count) | prompt | structured_model

    return chain


def create_mock_chain():
    """Create a mock chain for demonstration without API key."""

    def mock_summarize(input_dict: dict) -> SummaryOutput:
        text = input_dict.get("text", "")
        word_count = len(text.split())

        # Simple extraction for demo
        sentences = text.replace("\n", " ").split(".")
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        bullet_points = []
        for s in sentences[:3]:
            bullet_points.append(s[:100] + ("..." if len(s) > 100 else ""))

        # Pad if needed
        while len(bullet_points) < 3:
            bullet_points.append("Additional information not available")

        return SummaryOutput(
            main_topic="[Mock] " + (sentences[0][:50] if sentences else "Unknown topic"),
            bullet_points=bullet_points[:3],
            word_count=word_count
        )

    return RunnableLambda(mock_summarize)


def summarize_text(text: str) -> dict | None:
    """Summarize the given text.

    Args:
        text: The text to summarize

    Returns:
        Dictionary with main_topic, bullet_points, and word_count,
        or None if text is too short
    """
    # Validate text length
    word_count = len(text.split())
    if word_count < 50:
        print(f"Text too short ({word_count} words). Minimum 50 words required.")
        return None

    # Create and invoke the chain
    chain = create_summarization_chain()
    result = chain.invoke({"text": text})

    # Return as dict
    if isinstance(result, SummaryOutput):
        return result.model_dump()
    return result


# Test the implementation
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
    print("=" * 50)

    result = summarize_text(test_text)

    if result:
        print(f"\nMain Topic: {result['main_topic']}")
        print(f"\nBullet Points:")
        for i, point in enumerate(result['bullet_points'], 1):
            print(f"  {i}. {point}")
        print(f"\nWord Count: {result['word_count']}")
    else:
        print("Summarization failed.")

    # Test with short text
    print("\n" + "=" * 50)
    print("Testing with short text...")
    summarize_text("This is too short.")
