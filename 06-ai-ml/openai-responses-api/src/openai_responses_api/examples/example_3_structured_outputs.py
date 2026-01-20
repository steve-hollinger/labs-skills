"""
Example 3: Structured Outputs

This example demonstrates how to use OpenAI's structured output features
to get reliable, validated JSON responses matching a specific schema.

Key concepts:
- JSON mode for basic JSON responses
- Pydantic models for structured outputs
- Complex nested schemas
- Validation and error handling
"""

import os
from typing import Optional
from enum import Enum
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


# ============================================================================
# Pydantic Models for Structured Output
# ============================================================================

class Sentiment(str, Enum):
    """Sentiment classification."""
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class SentimentAnalysis(BaseModel):
    """Result of sentiment analysis."""
    sentiment: Sentiment = Field(description="Overall sentiment")
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")
    reasoning: str = Field(description="Brief explanation for the classification")


class Entity(BaseModel):
    """A named entity extracted from text."""
    name: str = Field(description="The entity name")
    type: str = Field(description="Entity type (person, organization, location, etc.)")
    relevance: float = Field(ge=0, le=1, description="Relevance score 0-1")


class TextAnalysis(BaseModel):
    """Complete text analysis result."""
    summary: str = Field(description="One-sentence summary")
    sentiment: SentimentAnalysis
    entities: list[Entity] = Field(default_factory=list)
    keywords: list[str] = Field(description="Key terms from the text")
    language: str = Field(description="Detected language code (e.g., 'en')")
    word_count: int = Field(description="Number of words in text")


class ProductInfo(BaseModel):
    """Extracted product information."""
    name: str
    price: Optional[float] = None
    currency: str = "USD"
    category: str
    features: list[str] = Field(default_factory=list)
    rating: Optional[float] = Field(None, ge=0, le=5)


class ContactInfo(BaseModel):
    """Extracted contact information."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None


# ============================================================================
# Client Setup
# ============================================================================

def get_client():
    """Get OpenAI client or mock."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Note: OPENAI_API_KEY not set. Using mock responses.")
        return None

    from openai import OpenAI
    return OpenAI()


# ============================================================================
# Structured Output Functions
# ============================================================================

def analyze_sentiment(text: str) -> SentimentAnalysis:
    """Analyze sentiment of text using structured output."""
    client = get_client()

    if client is None:
        # Mock response
        return SentimentAnalysis(
            sentiment=Sentiment.positive,
            confidence=0.85,
            reasoning="[Mock] Text appears generally positive"
        )

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Analyze the sentiment of the given text. Provide sentiment, confidence, and reasoning."
            },
            {"role": "user", "content": text}
        ],
        response_format=SentimentAnalysis
    )

    return response.choices[0].message.parsed


def analyze_text_complete(text: str) -> TextAnalysis:
    """Perform complete text analysis."""
    client = get_client()

    if client is None:
        # Mock response
        return TextAnalysis(
            summary="[Mock] This is a sample text analysis.",
            sentiment=SentimentAnalysis(
                sentiment=Sentiment.neutral,
                confidence=0.7,
                reasoning="Unable to determine without API"
            ),
            entities=[Entity(name="Example", type="concept", relevance=0.5)],
            keywords=["sample", "text", "analysis"],
            language="en",
            word_count=len(text.split())
        )

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Analyze the text comprehensively:
1. Provide a one-sentence summary
2. Analyze sentiment with confidence and reasoning
3. Extract named entities with types and relevance
4. Identify key terms
5. Detect language
6. Count words"""
            },
            {"role": "user", "content": text}
        ],
        response_format=TextAnalysis
    )

    return response.choices[0].message.parsed


def extract_product_info(description: str) -> ProductInfo:
    """Extract product information from description."""
    client = get_client()

    if client is None:
        return ProductInfo(
            name="[Mock] Sample Product",
            price=99.99,
            category="electronics",
            features=["Feature 1", "Feature 2"]
        )

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract product information from the description."
            },
            {"role": "user", "content": description}
        ],
        response_format=ProductInfo
    )

    return response.choices[0].message.parsed


def extract_contacts(text: str) -> list[ContactInfo]:
    """Extract contact information from text."""

    class ContactList(BaseModel):
        contacts: list[ContactInfo]

    client = get_client()

    if client is None:
        return [ContactInfo(
            name="John Doe",
            email="john@example.com",
            company="Example Corp"
        )]

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract all contact information from the text."
            },
            {"role": "user", "content": text}
        ],
        response_format=ContactList
    )

    return response.choices[0].message.parsed.contacts


# ============================================================================
# Examples
# ============================================================================

def example_sentiment_analysis():
    """Demonstrate sentiment analysis with structured output."""
    print("\n--- Sentiment Analysis ---")

    texts = [
        "I absolutely love this product! It exceeded all my expectations.",
        "The service was terrible and the staff was rude.",
        "The package arrived on time. It was as described.",
    ]

    for text in texts:
        result = analyze_sentiment(text)
        print(f"\nText: {text[:50]}...")
        print(f"  Sentiment: {result.sentiment.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Reasoning: {result.reasoning}")


def example_complete_analysis():
    """Demonstrate comprehensive text analysis."""
    print("\n--- Complete Text Analysis ---")

    text = """
    Apple Inc. announced today that CEO Tim Cook will present the new iPhone 16
    at their headquarters in Cupertino, California. The event is expected to
    showcase revolutionary AI features. Investors are excited about the potential
    impact on the company's stock price.
    """

    result = analyze_text_complete(text)

    print(f"\nSummary: {result.summary}")
    print(f"Language: {result.language}")
    print(f"Word count: {result.word_count}")
    print(f"\nSentiment: {result.sentiment.sentiment.value} ({result.sentiment.confidence:.2f})")
    print(f"Reasoning: {result.sentiment.reasoning}")
    print(f"\nKeywords: {', '.join(result.keywords)}")
    print(f"\nEntities ({len(result.entities)}):")
    for entity in result.entities:
        print(f"  - {entity.name} ({entity.type}): relevance {entity.relevance:.2f}")


def example_product_extraction():
    """Demonstrate product information extraction."""
    print("\n--- Product Information Extraction ---")

    description = """
    Introducing the TechPro Wireless Headphones - Premium noise-canceling
    over-ear headphones with 40-hour battery life. Features include Bluetooth 5.2,
    active noise cancellation, and premium memory foam ear cushions.
    Available for $299.99. Customer rating: 4.7 out of 5 stars.
    """

    result = extract_product_info(description)

    print(f"\nProduct: {result.name}")
    print(f"Price: {result.currency} {result.price}")
    print(f"Category: {result.category}")
    print(f"Rating: {result.rating}/5")
    print(f"Features:")
    for feature in result.features:
        print(f"  - {feature}")


def example_contact_extraction():
    """Demonstrate contact information extraction."""
    print("\n--- Contact Information Extraction ---")

    text = """
    For sales inquiries, please contact John Smith at john.smith@techcorp.com
    or call (555) 123-4567. He's the Senior Sales Manager at TechCorp.

    For support, reach out to Sarah Johnson, Customer Support Lead,
    at support@techcorp.com.
    """

    contacts = extract_contacts(text)

    print(f"\nExtracted {len(contacts)} contacts:")
    for i, contact in enumerate(contacts, 1):
        print(f"\n  Contact {i}:")
        if contact.name:
            print(f"    Name: {contact.name}")
        if contact.title:
            print(f"    Title: {contact.title}")
        if contact.company:
            print(f"    Company: {contact.company}")
        if contact.email:
            print(f"    Email: {contact.email}")
        if contact.phone:
            print(f"    Phone: {contact.phone}")


def example_json_mode():
    """Demonstrate basic JSON mode (without schema enforcement)."""
    print("\n--- Basic JSON Mode ---")

    client = get_client()

    if client is None:
        print("  Skipping JSON mode demo (requires real API)")
        return

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Always respond with valid JSON containing 'items' array."
            },
            {"role": "user", "content": "List 3 programming languages with their main use cases."}
        ],
        response_format={"type": "json_object"}
    )

    import json
    result = json.loads(response.choices[0].message.content)
    print(f"\nJSON response:")
    print(json.dumps(result, indent=2))


def main():
    """Run all structured output examples."""
    print("=" * 60)
    print("Example 3: Structured Outputs")
    print("=" * 60)

    example_sentiment_analysis()
    example_complete_analysis()
    example_product_extraction()
    example_contact_extraction()
    example_json_mode()

    print("\n" + "=" * 60)
    print("Key Takeaways:")
    print("1. Use Pydantic models to define output schemas")
    print("2. beta.chat.completions.parse ensures valid responses")
    print("3. Complex nested schemas are fully supported")
    print("4. Structured outputs eliminate JSON parsing errors")
    print("=" * 60)


if __name__ == "__main__":
    main()
