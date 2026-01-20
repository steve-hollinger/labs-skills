"""
Example 3: LangGraph Workflow

This example demonstrates how to build stateful, multi-step workflows using LangGraph.
We'll create a document processing pipeline that validates, analyzes, and summarizes text.

Key concepts:
- StateGraph for defining workflows
- TypedDict for state definition
- Nodes as processing functions
- Conditional routing between nodes
- Graph compilation and execution
"""

import os
from typing import TypedDict, Annotated, Literal
from operator import add
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END

# Load environment variables
load_dotenv()


# ============================================================================
# State Definition
# ============================================================================

class DocumentState(TypedDict):
    """State for document processing workflow.

    Attributes:
        document: The input document text
        is_valid: Whether the document passed validation
        validation_message: Message from validation step
        word_count: Number of words in the document
        sentiment: Detected sentiment (positive/negative/neutral)
        key_topics: Extracted key topics
        summary: Final summary of the document
        processing_log: Log of processing steps (accumulates)
        error: Any error that occurred
    """
    document: str
    is_valid: bool
    validation_message: str
    word_count: int
    sentiment: str
    key_topics: list[str]
    summary: str
    processing_log: Annotated[list[str], add]  # Accumulates entries
    error: str | None


# ============================================================================
# Node Functions
# ============================================================================

def validate_document(state: DocumentState) -> dict:
    """Validate the input document."""
    document = state["document"]

    # Check minimum length
    if len(document.strip()) < 10:
        return {
            "is_valid": False,
            "validation_message": "Document too short (minimum 10 characters)",
            "processing_log": ["Validation failed: document too short"]
        }

    # Check for actual content (not just whitespace or punctuation)
    word_count = len(document.split())
    if word_count < 3:
        return {
            "is_valid": False,
            "validation_message": "Document must contain at least 3 words",
            "processing_log": ["Validation failed: insufficient words"]
        }

    return {
        "is_valid": True,
        "validation_message": "Document validated successfully",
        "word_count": word_count,
        "processing_log": [f"Validation passed: {word_count} words"]
    }


def analyze_sentiment(state: DocumentState) -> dict:
    """Analyze the sentiment of the document."""
    document = state["document"].lower()

    # Simple keyword-based sentiment analysis (mock)
    positive_words = ["good", "great", "excellent", "happy", "love", "wonderful", "amazing", "best"]
    negative_words = ["bad", "terrible", "awful", "hate", "worst", "horrible", "sad", "angry"]

    positive_count = sum(1 for word in positive_words if word in document)
    negative_count = sum(1 for word in negative_words if word in document)

    if positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "processing_log": [f"Sentiment analysis complete: {sentiment}"]
    }


def extract_topics(state: DocumentState) -> dict:
    """Extract key topics from the document."""
    document = state["document"].lower()

    # Simple topic extraction (mock)
    topic_keywords = {
        "technology": ["software", "computer", "ai", "machine learning", "programming", "code"],
        "business": ["company", "market", "revenue", "profit", "business", "startup"],
        "science": ["research", "study", "experiment", "data", "analysis", "scientific"],
        "health": ["health", "medical", "doctor", "patient", "treatment", "disease"],
        "education": ["learning", "school", "student", "teacher", "education", "course"],
    }

    found_topics = []
    for topic, keywords in topic_keywords.items():
        if any(keyword in document for keyword in keywords):
            found_topics.append(topic)

    if not found_topics:
        found_topics = ["general"]

    return {
        "key_topics": found_topics,
        "processing_log": [f"Topics extracted: {', '.join(found_topics)}"]
    }


def generate_summary_mock(state: DocumentState) -> dict:
    """Generate a summary without LLM (mock version)."""
    document = state["document"]
    sentiment = state["sentiment"]
    topics = state["key_topics"]
    word_count = state["word_count"]

    summary = (
        f"Document Summary:\n"
        f"- Length: {word_count} words\n"
        f"- Sentiment: {sentiment}\n"
        f"- Topics: {', '.join(topics)}\n"
        f"- Preview: {document[:100]}..."
    )

    return {
        "summary": summary,
        "processing_log": ["Summary generated (mock)"]
    }


def generate_summary_llm(state: DocumentState) -> dict:
    """Generate a summary using LLM."""
    from langchain_openai import ChatOpenAI

    document = state["document"]
    sentiment = state["sentiment"]
    topics = state["key_topics"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a document summarizer. Create a concise summary."),
        ("user", """Summarize this document in 2-3 sentences.

Document: {document}

Context:
- Detected sentiment: {sentiment}
- Key topics: {topics}

Summary:""")
    ])

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    parser = StrOutputParser()

    chain = prompt | model | parser

    summary = chain.invoke({
        "document": document,
        "sentiment": sentiment,
        "topics": ", ".join(topics)
    })

    return {
        "summary": summary,
        "processing_log": ["Summary generated (LLM)"]
    }


def handle_invalid_document(state: DocumentState) -> dict:
    """Handle invalid documents."""
    return {
        "summary": f"Could not process document: {state['validation_message']}",
        "processing_log": ["Processing terminated: invalid document"]
    }


# ============================================================================
# Routing Functions
# ============================================================================

def route_after_validation(state: DocumentState) -> Literal["analyze", "invalid"]:
    """Route based on validation result."""
    if state["is_valid"]:
        return "analyze"
    return "invalid"


# ============================================================================
# Graph Construction
# ============================================================================

def create_document_workflow(use_llm: bool = False) -> StateGraph:
    """Create the document processing workflow graph.

    Args:
        use_llm: Whether to use LLM for summary generation

    Returns:
        Compiled workflow graph
    """
    # Create the graph with our state type
    workflow = StateGraph(DocumentState)

    # Add nodes
    workflow.add_node("validate", validate_document)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("extract_topics", extract_topics)

    # Choose summary function based on LLM availability
    if use_llm and os.getenv("OPENAI_API_KEY"):
        workflow.add_node("summarize", generate_summary_llm)
    else:
        workflow.add_node("summarize", generate_summary_mock)

    workflow.add_node("handle_invalid", handle_invalid_document)

    # Add edges
    workflow.add_edge(START, "validate")

    # Conditional routing after validation
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "analyze": "analyze_sentiment",
            "invalid": "handle_invalid"
        }
    )

    # Linear flow for valid documents
    workflow.add_edge("analyze_sentiment", "extract_topics")
    workflow.add_edge("extract_topics", "summarize")

    # Both paths end
    workflow.add_edge("summarize", END)
    workflow.add_edge("handle_invalid", END)

    # Compile and return
    return workflow.compile()


# ============================================================================
# Demonstration
# ============================================================================

def process_document(workflow, document: str, title: str = "Document"):
    """Process a document through the workflow."""
    print(f"\n{'=' * 50}")
    print(f"Processing: {title}")
    print(f"{'=' * 50}")
    print(f"Input: {document[:100]}{'...' if len(document) > 100 else ''}")
    print("-" * 50)

    # Initialize state
    initial_state = {
        "document": document,
        "is_valid": False,
        "validation_message": "",
        "word_count": 0,
        "sentiment": "",
        "key_topics": [],
        "summary": "",
        "processing_log": ["Processing started"],
        "error": None
    }

    # Run the workflow
    result = workflow.invoke(initial_state)

    # Display results
    print("\nProcessing Log:")
    for entry in result["processing_log"]:
        print(f"  - {entry}")

    print(f"\nFinal Summary:\n{result['summary']}")

    return result


def main():
    """Run the LangGraph workflow examples."""
    print("=" * 60)
    print("Example 3: LangGraph Document Processing Workflow")
    print("=" * 60)

    # Create the workflow
    use_llm = bool(os.getenv("OPENAI_API_KEY"))
    if not use_llm:
        print("\nNote: OPENAI_API_KEY not set. Using mock summary generation.")

    workflow = create_document_workflow(use_llm=use_llm)

    # Test documents
    documents = [
        # Valid positive document
        (
            "This is an excellent software product that makes programming much easier. "
            "The machine learning features are amazing and the AI capabilities are wonderful. "
            "I love how it handles data analysis.",
            "Positive Tech Review"
        ),
        # Valid negative document
        (
            "The company reported terrible revenue numbers this quarter. "
            "The market response was awful and investors are angry. "
            "The business outlook looks bad.",
            "Negative Business News"
        ),
        # Valid neutral document
        (
            "The research study examined patient data from multiple hospitals. "
            "The scientific analysis included treatment protocols and medical outcomes. "
            "Further research is needed to draw conclusions.",
            "Neutral Scientific Paper"
        ),
        # Invalid document (too short)
        (
            "Hi there!",
            "Too Short"
        ),
    ]

    for document, title in documents:
        process_document(workflow, document, title)

    # Demonstrate streaming updates
    print("\n" + "=" * 60)
    print("Streaming Workflow Updates")
    print("=" * 60)

    test_doc = "Learning is essential for students. Every school and teacher plays a vital role in education."

    print(f"\nProcessing with streaming: '{test_doc}'")
    print("-" * 50)

    initial_state = {
        "document": test_doc,
        "is_valid": False,
        "validation_message": "",
        "word_count": 0,
        "sentiment": "",
        "key_topics": [],
        "summary": "",
        "processing_log": ["Processing started"],
        "error": None
    }

    # Stream updates
    for update in workflow.stream(initial_state):
        node_name = list(update.keys())[0]
        print(f"\nNode completed: {node_name}")
        if "processing_log" in update[node_name]:
            print(f"  Log: {update[node_name]['processing_log']}")

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. StateGraph defines the workflow structure")
    print("2. TypedDict enforces state schema")
    print("3. Nodes are functions that update state")
    print("4. Conditional edges enable dynamic routing")
    print("5. stream() provides real-time progress updates")
    print("=" * 60)


if __name__ == "__main__":
    main()
