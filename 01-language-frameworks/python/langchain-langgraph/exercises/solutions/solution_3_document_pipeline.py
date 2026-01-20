"""
Solution 3: Document Processing Pipeline with LangGraph

This solution demonstrates how to build a complete document processing
pipeline with conditional routing, multiple processing paths, and error handling.
"""

import os
import re
from typing import TypedDict, Annotated, Literal
from operator import add
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

load_dotenv()


class DocumentPipelineState(TypedDict):
    """State for document processing pipeline."""
    document: str
    is_valid: bool
    validation_errors: list[str]
    detected_language: str
    content_type: str
    processed_content: str
    processing_log: Annotated[list[str], add]
    final_report: str
    error: str | None


# Node implementations

def validate_document(state: DocumentPipelineState) -> dict:
    """Validate the input document."""
    document = state["document"]
    errors = []

    # Check minimum length
    if len(document.strip()) < 20:
        errors.append("Document too short (minimum 20 characters)")

    # Check for actual content
    words = document.split()
    if len(words) < 5:
        errors.append("Document must contain at least 5 words")

    # Check for non-trivial content (not just numbers/symbols)
    alpha_words = [w for w in words if any(c.isalpha() for c in w)]
    if len(alpha_words) < 3:
        errors.append("Document must contain meaningful text content")

    if errors:
        return {
            "is_valid": False,
            "validation_errors": errors,
            "processing_log": [f"Validation FAILED: {'; '.join(errors)}"]
        }

    return {
        "is_valid": True,
        "validation_errors": [],
        "processing_log": [f"Validation PASSED: {len(words)} words, {len(document)} characters"]
    }


def detect_language(state: DocumentPipelineState) -> dict:
    """Detect the language of the document."""
    document = state["document"].lower()

    # Language indicators
    language_markers = {
        "en": ["the", "is", "are", "and", "or", "that", "this", "with", "for", "have"],
        "es": ["el", "la", "es", "y", "o", "de", "que", "en", "los", "las"],
        "fr": ["le", "la", "est", "et", "ou", "de", "que", "les", "des", "un"],
        "de": ["der", "die", "das", "und", "ist", "ein", "eine", "mit", "von", "zu"],
    }

    # Count matches for each language
    scores = {}
    words = set(re.findall(r'\b\w+\b', document))

    for lang, markers in language_markers.items():
        score = sum(1 for marker in markers if marker in words)
        scores[lang] = score

    # Get best match
    detected = max(scores, key=scores.get)
    confidence = scores[detected]

    # Default to English if low confidence
    if confidence < 2:
        detected = "en"

    language_names = {"en": "English", "es": "Spanish", "fr": "French", "de": "German"}

    return {
        "detected_language": detected,
        "processing_log": [f"Language detected: {language_names.get(detected, detected)} (confidence: {confidence})"]
    }


def classify_content(state: DocumentPipelineState) -> dict:
    """Classify the content type."""
    document = state["document"].lower()

    # Classification keywords
    classifications = {
        "technical": [
            "software", "code", "programming", "algorithm", "data", "system",
            "function", "api", "database", "server", "application", "technology"
        ],
        "business": [
            "revenue", "profit", "market", "sales", "company", "business",
            "growth", "investment", "quarter", "financial", "strategy", "customer"
        ],
    }

    # Score each category
    scores = {}
    for category, keywords in classifications.items():
        score = sum(1 for kw in keywords if kw in document)
        scores[category] = score

    # Determine classification
    max_score = max(scores.values())
    if max_score >= 2:
        content_type = max(scores, key=scores.get)
    else:
        content_type = "general"

    return {
        "content_type": content_type,
        "processing_log": [f"Content classified as: {content_type.upper()}"]
    }


def process_technical(state: DocumentPipelineState) -> dict:
    """Process technical content."""
    document = state["document"]

    # Extract technical terms
    tech_terms = [
        "software", "code", "programming", "algorithm", "data", "system",
        "api", "database", "server", "application", "function", "module",
        "framework", "library", "architecture", "interface", "protocol"
    ]

    found_terms = [term for term in tech_terms if term in document.lower()]
    word_count = len(document.split())
    sentence_count = len([s for s in document.split('.') if s.strip()])

    processed = f"""Technical Document Analysis:
- Word count: {word_count}
- Sentence count: {sentence_count}
- Technical terms found: {', '.join(found_terms) if found_terms else 'None identified'}
- Technical density: {len(found_terms) / max(1, word_count) * 100:.1f}% of words are technical terms"""

    return {
        "processed_content": processed,
        "processing_log": ["Technical processing complete"]
    }


def process_business(state: DocumentPipelineState) -> dict:
    """Process business content."""
    document = state["document"]

    # Extract business metrics (mock - looking for numbers with context)
    metrics_pattern = r'(\d+(?:\.\d+)?)\s*(%|percent|million|billion|thousand)?'
    metrics = re.findall(metrics_pattern, document)

    business_terms = [
        "revenue", "profit", "growth", "sales", "market", "strategy",
        "investment", "performance", "quarter", "year", "forecast"
    ]

    found_terms = [term for term in business_terms if term in document.lower()]
    word_count = len(document.split())

    processed = f"""Business Document Analysis:
- Word count: {word_count}
- Numeric metrics found: {len(metrics)}
- Business terms identified: {', '.join(found_terms) if found_terms else 'None identified'}
- Key focus areas: {', '.join(found_terms[:3]) if found_terms else 'General business'}"""

    return {
        "processed_content": processed,
        "processing_log": ["Business processing complete"]
    }


def process_general(state: DocumentPipelineState) -> dict:
    """Process general content."""
    document = state["document"]

    word_count = len(document.split())
    sentence_count = len([s for s in document.split('.') if s.strip()])
    paragraph_count = len([p for p in document.split('\n\n') if p.strip()])

    # Create a simple summary (first sentence or first 100 chars)
    sentences = [s.strip() for s in document.split('.') if s.strip()]
    preview = sentences[0][:100] if sentences else document[:100]

    processed = f"""General Document Analysis:
- Word count: {word_count}
- Sentence count: {sentence_count}
- Paragraph count: {max(1, paragraph_count)}
- Average words per sentence: {word_count / max(1, sentence_count):.1f}
- Preview: {preview}..."""

    return {
        "processed_content": processed,
        "processing_log": ["General processing complete"]
    }


def translate_placeholder(state: DocumentPipelineState) -> dict:
    """Placeholder for translation."""
    lang = state["detected_language"]
    language_names = {"es": "Spanish", "fr": "French", "de": "German"}

    return {
        "processing_log": [
            f"Translation needed: Document is in {language_names.get(lang, lang)}",
            "Note: Translation would be performed here in production"
        ]
    }


def generate_report(state: DocumentPipelineState) -> dict:
    """Generate the final processing report."""
    report = f"""
================================================================================
                        DOCUMENT PROCESSING REPORT
================================================================================

VALIDATION: {"PASSED" if state["is_valid"] else "FAILED"}
{chr(10).join('  - ' + e for e in state.get("validation_errors", [])) if state.get("validation_errors") else "  - No errors"}

LANGUAGE: {state.get("detected_language", "Unknown").upper()}

CLASSIFICATION: {state.get("content_type", "Unknown").upper()}

ANALYSIS:
{state.get("processed_content", "No analysis available")}

PROCESSING LOG:
{chr(10).join('  ' + str(i+1) + '. ' + log for i, log in enumerate(state.get("processing_log", [])))}

================================================================================
"""

    return {"final_report": report}


def handle_error(state: DocumentPipelineState) -> dict:
    """Handle validation or processing errors."""
    errors = state.get("validation_errors", ["Unknown error"])

    report = f"""
================================================================================
                        DOCUMENT PROCESSING REPORT
================================================================================

STATUS: FAILED

VALIDATION ERRORS:
{chr(10).join('  - ' + e for e in errors)}

PROCESSING LOG:
{chr(10).join('  ' + str(i+1) + '. ' + log for i, log in enumerate(state.get("processing_log", [])))}

RECOMMENDATION:
  Please ensure your document:
  - Contains at least 20 characters
  - Has at least 5 words
  - Includes meaningful text content (not just numbers/symbols)

================================================================================
"""

    return {"final_report": report}


# Routing functions

def route_after_validation(state: DocumentPipelineState) -> Literal["valid", "invalid"]:
    """Route based on validation result."""
    return "valid" if state["is_valid"] else "invalid"


def route_after_language(state: DocumentPipelineState) -> Literal["english", "other"]:
    """Route based on detected language."""
    return "english" if state["detected_language"] == "en" else "other"


def route_after_classification(state: DocumentPipelineState) -> Literal["technical", "business", "general"]:
    """Route based on content classification."""
    content_type = state.get("content_type", "general")
    if content_type in ["technical", "business"]:
        return content_type
    return "general"


def create_document_pipeline() -> StateGraph:
    """Create the document processing pipeline."""
    workflow = StateGraph(DocumentPipelineState)

    # Add all nodes
    workflow.add_node("validate", validate_document)
    workflow.add_node("detect_language", detect_language)
    workflow.add_node("classify_content", classify_content)
    workflow.add_node("translate", translate_placeholder)
    workflow.add_node("process_technical", process_technical)
    workflow.add_node("process_business", process_business)
    workflow.add_node("process_general", process_general)
    workflow.add_node("generate_report", generate_report)
    workflow.add_node("handle_error", handle_error)

    # Start -> validate
    workflow.add_edge(START, "validate")

    # Validation routing
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {"valid": "detect_language", "invalid": "handle_error"}
    )

    # Language routing
    workflow.add_conditional_edges(
        "detect_language",
        route_after_language,
        {"english": "classify_content", "other": "translate"}
    )

    # Translation -> classification
    workflow.add_edge("translate", "classify_content")

    # Classification routing
    workflow.add_conditional_edges(
        "classify_content",
        route_after_classification,
        {
            "technical": "process_technical",
            "business": "process_business",
            "general": "process_general"
        }
    )

    # Processing -> report
    workflow.add_edge("process_technical", "generate_report")
    workflow.add_edge("process_business", "generate_report")
    workflow.add_edge("process_general", "generate_report")

    # End nodes
    workflow.add_edge("generate_report", END)
    workflow.add_edge("handle_error", END)

    return workflow.compile()


def process_document(document: str) -> dict:
    """Process a document through the pipeline."""
    pipeline = create_document_pipeline()

    initial_state = {
        "document": document,
        "is_valid": False,
        "validation_errors": [],
        "detected_language": "",
        "content_type": "",
        "processed_content": "",
        "processing_log": ["Pipeline started"],
        "final_report": "",
        "error": None
    }

    return pipeline.invoke(initial_state)


# Test the implementation
if __name__ == "__main__":
    test_documents = [
        # Valid technical document
        ("""
        The new software architecture uses microservices and containerization.
        Our programming team implemented the algorithm using Python code.
        The system processes data through multiple pipeline stages.
        The API provides a clean interface for external applications.
        """, "Technical Document"),

        # Valid business document
        ("""
        Q3 revenue exceeded expectations with strong market performance.
        Sales grew 15% and profit margins improved significantly.
        The company plans to expand into new markets next quarter.
        Investment in customer acquisition continues to drive growth.
        """, "Business Document"),

        # Valid general document
        ("""
        The weather today was beautiful with clear blue skies.
        Many people enjoyed walking in the park and having picnics.
        It was a perfect day for outdoor activities and relaxation.
        """, "General Document"),

        # Invalid document (too short)
        ("Hello", "Short Document"),

        # Non-English document (Spanish)
        ("""
        El nuevo sistema de software utiliza microservicios y contenedores.
        La arquitectura es muy moderna y eficiente para las aplicaciones.
        Nuestro equipo de programacion trabaja con Python y bases de datos.
        """, "Spanish Document"),
    ]

    print("Testing Document Processing Pipeline")
    print("=" * 80)

    for doc, title in test_documents:
        print(f"\n{'='*80}")
        print(f"Processing: {title}")
        print(f"Input preview: {doc[:80].strip()}...")
        print(f"{'='*80}")

        result = process_document(doc)
        print(result["final_report"])
