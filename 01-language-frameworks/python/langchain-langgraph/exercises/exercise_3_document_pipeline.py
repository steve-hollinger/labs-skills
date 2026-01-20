"""
Exercise 3: Build a Document Processing Pipeline with LangGraph

Create a LangGraph workflow that processes documents through multiple stages
with conditional routing and error handling.

Requirements:
1. Define a state schema for document processing
2. Create nodes for:
   - Document validation
   - Language detection
   - Content classification (technical, business, general)
   - Appropriate processing based on classification
3. Implement conditional routing based on:
   - Validation result (valid/invalid)
   - Detected language (English/other)
   - Content type (routes to different processors)
4. Add error handling for each step
5. Include a final report generation node

Workflow visualization:
                    START
                      |
                  [validate]
                   /     \
            invalid       valid
              |             |
        [error_report]  [detect_language]
              |            /       \
             END      english     other
                        |           |
               [classify_content]  [translate_first]
                  /    |    \          |
           tech  biz  general    [classify_content]
             |    |      |
       [process_tech] [process_biz] [process_general]
                  \      |       /
                   [generate_report]
                         |
                        END

Hints:
- Use TypedDict with Annotated for accumulating fields
- add_conditional_edges for routing decisions
- Return only the fields you want to update from each node
- Use Literal type hints for routing functions
"""

import os
from typing import TypedDict, Annotated, Literal
from operator import add
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

load_dotenv()


# TODO: Define the state schema
class DocumentPipelineState(TypedDict):
    """State for document processing pipeline.

    Define these fields:
    - document: str - The input document text
    - is_valid: bool - Whether validation passed
    - validation_errors: list[str] - Any validation errors
    - detected_language: str - Detected language code (en, es, fr, etc.)
    - content_type: str - Classification (technical, business, general)
    - processed_content: str - Result of content processing
    - processing_log: Annotated[list[str], add] - Accumulating log
    - final_report: str - Final processing report
    - error: str | None - Any error message
    """
    pass


# TODO: Implement node functions

def validate_document(state: DocumentPipelineState) -> dict:
    """Validate the input document.

    Check for:
    - Minimum length (at least 20 characters)
    - Not empty after stripping whitespace
    - Contains actual words (not just numbers/symbols)

    Returns:
        Dict with is_valid, validation_errors, and processing_log update
    """
    pass


def detect_language(state: DocumentPipelineState) -> dict:
    """Detect the language of the document.

    Simple detection based on common words:
    - English: the, is, are, and, or
    - Spanish: el, la, es, y, o, de
    - French: le, la, est, et, ou, de

    Returns:
        Dict with detected_language and processing_log update
    """
    pass


def classify_content(state: DocumentPipelineState) -> dict:
    """Classify the content type.

    Categories:
    - technical: Contains words like code, software, algorithm, programming
    - business: Contains words like revenue, profit, market, sales
    - general: Everything else

    Returns:
        Dict with content_type and processing_log update
    """
    pass


def process_technical(state: DocumentPipelineState) -> dict:
    """Process technical content.

    For technical documents, extract:
    - Code-related terms
    - Technical concepts mentioned

    Returns:
        Dict with processed_content and processing_log update
    """
    pass


def process_business(state: DocumentPipelineState) -> dict:
    """Process business content.

    For business documents, extract:
    - Business metrics mentioned
    - Key business terms

    Returns:
        Dict with processed_content and processing_log update
    """
    pass


def process_general(state: DocumentPipelineState) -> dict:
    """Process general content.

    For general documents:
    - Create a brief summary
    - Count sentences and paragraphs

    Returns:
        Dict with processed_content and processing_log update
    """
    pass


def translate_placeholder(state: DocumentPipelineState) -> dict:
    """Placeholder for translation (mock).

    In a real system, this would translate to English.
    For this exercise, just note that translation would be needed.

    Returns:
        Dict with processing_log update noting translation needed
    """
    pass


def generate_report(state: DocumentPipelineState) -> dict:
    """Generate the final processing report.

    Include:
    - Document statistics
    - Language detected
    - Content classification
    - Processing result
    - Full processing log

    Returns:
        Dict with final_report
    """
    pass


def handle_error(state: DocumentPipelineState) -> dict:
    """Handle validation or processing errors.

    Generate an error report explaining what went wrong.

    Returns:
        Dict with final_report containing error information
    """
    pass


# TODO: Implement routing functions

def route_after_validation(state: DocumentPipelineState) -> Literal["valid", "invalid"]:
    """Route based on validation result."""
    pass


def route_after_language(state: DocumentPipelineState) -> Literal["english", "other"]:
    """Route based on detected language."""
    pass


def route_after_classification(state: DocumentPipelineState) -> Literal["technical", "business", "general"]:
    """Route based on content classification."""
    pass


# TODO: Build the workflow

def create_document_pipeline() -> StateGraph:
    """Create the document processing pipeline.

    Build the graph with:
    1. All nodes added
    2. START -> validate edge
    3. Conditional edges after validate (valid/invalid)
    4. Conditional edges after language detection (english/other)
    5. Conditional edges after classification (technical/business/general)
    6. All processing nodes -> generate_report
    7. generate_report -> END
    8. handle_error -> END

    Returns:
        Compiled StateGraph
    """
    pass


def process_document(document: str) -> dict:
    """Process a document through the pipeline.

    Args:
        document: The document text to process

    Returns:
        The final state including the report
    """
    # TODO: Implement
    # 1. Create the pipeline
    # 2. Initialize state
    # 3. Invoke and return result
    pass


# Test your implementation
if __name__ == "__main__":
    test_documents = [
        # Valid technical document
        """
        The new software architecture uses microservices and containerization.
        Our programming team implemented the algorithm using Python code.
        The system processes data through multiple pipeline stages.
        """,

        # Valid business document
        """
        Q3 revenue exceeded expectations with strong market performance.
        Sales grew 15% and profit margins improved significantly.
        The company plans to expand into new markets next quarter.
        """,

        # Valid general document
        """
        The weather today was beautiful with clear blue skies.
        Many people enjoyed walking in the park and having picnics.
        It was a perfect day for outdoor activities.
        """,

        # Invalid document (too short)
        "Hello",

        # Non-English document (Spanish)
        """
        El nuevo sistema de software utiliza microservicios.
        La arquitectura es muy moderna y eficiente.
        """,
    ]

    print("Testing Document Processing Pipeline")
    print("=" * 60)

    for i, doc in enumerate(test_documents, 1):
        print(f"\n--- Document {i} ---")
        print(f"Input: {doc[:100].strip()}...")

        result = process_document(doc)
        if result:
            print(f"\nFinal Report:\n{result.get('final_report', 'No report')}")
        else:
            print("\nPipeline not implemented yet.")

        print("-" * 60)
