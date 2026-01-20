"""
Example 1: Simple Chain with LCEL

This example demonstrates the fundamentals of LangChain Expression Language (LCEL)
for building chains that process input through prompts, models, and output parsers.

Key concepts:
- ChatPromptTemplate for structuring prompts
- ChatOpenAI for model interaction
- StrOutputParser for extracting text output
- Pipe operator (|) for composition
"""

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()


def create_simple_chain():
    """Create a simple chain that answers questions."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Note: OPENAI_API_KEY not set. Using mock model for demonstration.")
        return create_mock_chain()

    from langchain_openai import ChatOpenAI

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that provides concise answers."),
        ("user", "{question}")
    ])

    # Initialize the model
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=500
    )

    # Create the output parser
    output_parser = StrOutputParser()

    # Compose the chain using LCEL pipe operator
    chain = prompt | model | output_parser

    return chain


def create_mock_chain():
    """Create a mock chain for demonstration without API key."""
    from langchain_core.runnables import RunnableLambda

    def mock_response(input_dict: dict) -> str:
        question = input_dict.get("question", "")
        return f"[Mock Response] You asked: '{question}'. This is a simulated response."

    return RunnableLambda(mock_response)


def create_multi_step_chain():
    """Create a chain with multiple processing steps."""
    if not os.getenv("OPENAI_API_KEY"):
        print("Note: OPENAI_API_KEY not set. Using mock chain.")
        return create_mock_chain()

    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    output_parser = StrOutputParser()

    # Step 1: Analyze the question
    analyze_prompt = ChatPromptTemplate.from_messages([
        ("system", "Analyze the following question and identify the key topics."),
        ("user", "Question: {question}\n\nKey topics:")
    ])

    # Step 2: Generate a detailed answer
    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert assistant. Provide a detailed answer."),
        ("user", "Topics: {topics}\n\nOriginal question: {question}\n\nDetailed answer:")
    ])

    # Chain step 1
    analyze_chain = analyze_prompt | model | output_parser

    # Combined chain using a lambda to pass data between steps
    def multi_step(input_dict: dict) -> str:
        question = input_dict["question"]
        topics = analyze_chain.invoke({"question": question})
        answer_chain = answer_prompt | model | output_parser
        return answer_chain.invoke({"topics": topics, "question": question})

    from langchain_core.runnables import RunnableLambda
    return RunnableLambda(multi_step)


def demonstrate_streaming():
    """Demonstrate streaming responses."""
    if not os.getenv("OPENAI_API_KEY"):
        print("Note: Streaming requires OPENAI_API_KEY.")
        return

    from langchain_openai import ChatOpenAI

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a storyteller."),
        ("user", "Tell a very short story about {topic}.")
    ])

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.9)
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser

    print("\n--- Streaming Response ---")
    for chunk in chain.stream({"topic": "a curious robot"}):
        print(chunk, end="", flush=True)
    print("\n")


def main():
    """Run the simple chain examples."""
    print("=" * 60)
    print("Example 1: Simple Chain with LCEL")
    print("=" * 60)

    # Example 1: Basic chain
    print("\n--- Basic Chain ---")
    chain = create_simple_chain()
    response = chain.invoke({"question": "What is LangChain in one sentence?"})
    print(f"Question: What is LangChain in one sentence?")
    print(f"Response: {response}")

    # Example 2: Multi-step chain
    print("\n--- Multi-Step Chain ---")
    multi_chain = create_multi_step_chain()
    response = multi_chain.invoke({
        "question": "How does machine learning differ from traditional programming?"
    })
    print(f"Question: How does machine learning differ from traditional programming?")
    print(f"Response: {response}")

    # Example 3: Streaming (if API key available)
    demonstrate_streaming()

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. Use ChatPromptTemplate for structured prompts")
    print("2. Compose chains with the pipe operator (|)")
    print("3. StrOutputParser extracts text from model responses")
    print("4. Use .stream() for real-time token output")
    print("=" * 60)


if __name__ == "__main__":
    main()
