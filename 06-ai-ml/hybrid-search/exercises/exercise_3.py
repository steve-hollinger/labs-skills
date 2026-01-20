"""Exercise 3: Build a FAQ Hybrid Search System

In this exercise, you'll build a complete hybrid search system for
a customer support FAQ database. This combines everything learned.

Instructions:
1. Implement the `FAQSearcher` class with vector and keyword search
2. Implement hybrid search with RRF fusion
3. Add category filtering to search results
4. Create a relevance feedback mechanism

Expected Output:
When you run this file, the search results should be relevant and
properly ranked.

Hints:
- Use sentence-transformers for embeddings
- Use rank-bm25 for keyword search
- RRF formula: sum(1 / (k + rank)) for each ranker
- Filter by category after fusion, not before
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class FAQItem:
    """A FAQ item with question, answer, and metadata."""

    id: int
    question: str
    answer: str
    category: str
    keywords: list[str]


@dataclass
class SearchResult:
    """Search result with score and explanation."""

    faq: FAQItem
    score: float
    vector_rank: int
    keyword_rank: int


class FAQSearcher:
    """Hybrid search system for FAQ database."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initialize the FAQ searcher.

        TODO: Initialize:
        - Sentence transformer model
        - Empty lists for FAQs, embeddings
        - BM25 index placeholder
        """
        # TODO: Implement initialization
        pass

    def add_faqs(self, faqs: list[FAQItem]) -> None:
        """Add FAQs to the search index.

        TODO:
        1. Store FAQs
        2. Create combined text (question + answer) for each FAQ
        3. Generate embeddings for combined text
        4. Build BM25 index from combined text
        """
        # TODO: Implement this method
        pass

    def _get_vector_ranking(self, query: str) -> list[int]:
        """Get FAQ IDs ranked by vector similarity.

        TODO:
        1. Encode query
        2. Compute cosine similarity with all FAQ embeddings
        3. Return indices sorted by similarity (descending)
        """
        # TODO: Implement this method
        pass

    def _get_keyword_ranking(self, query: str) -> list[int]:
        """Get FAQ IDs ranked by BM25 score.

        TODO:
        1. Tokenize query
        2. Get BM25 scores
        3. Return indices sorted by score (descending)
        """
        # TODO: Implement this method
        pass

    def _reciprocal_rank_fusion(
        self,
        vector_ranking: list[int],
        keyword_ranking: list[int],
        k: int = 60,
    ) -> list[tuple[int, float]]:
        """Combine rankings using RRF.

        TODO:
        1. For each FAQ ID in both rankings
        2. Compute RRF score: 1/(k + vector_rank) + 1/(k + keyword_rank)
        3. Return sorted by RRF score descending
        """
        # TODO: Implement this method
        pass

    def search(
        self,
        query: str,
        top_k: int = 5,
        category: str | None = None,
    ) -> list[SearchResult]:
        """Search FAQs with hybrid ranking.

        TODO:
        1. Get vector and keyword rankings
        2. Apply RRF fusion
        3. Filter by category if specified
        4. Return top_k results with scores and rank info
        """
        # TODO: Implement this method
        pass

    def get_related_faqs(self, faq_id: int, top_k: int = 3) -> list[SearchResult]:
        """Find FAQs related to a given FAQ.

        TODO:
        1. Get the FAQ by ID
        2. Use its question as a query
        3. Search and filter out the original FAQ
        """
        # TODO: Implement this method
        pass


def create_sample_faqs() -> list[FAQItem]:
    """Create sample FAQ database."""
    return [
        FAQItem(
            id=0,
            question="How do I reset my password?",
            answer="Go to Settings > Security > Reset Password and follow the prompts.",
            category="account",
            keywords=["password", "reset", "security"],
        ),
        FAQItem(
            id=1,
            question="What payment methods do you accept?",
            answer="We accept Visa, Mastercard, American Express, PayPal, and Apple Pay.",
            category="billing",
            keywords=["payment", "credit card", "paypal"],
        ),
        FAQItem(
            id=2,
            question="How can I contact customer support?",
            answer="Email support@example.com, call 1-800-123-4567, or use live chat.",
            category="support",
            keywords=["contact", "support", "help"],
        ),
        FAQItem(
            id=3,
            question="What is your refund policy?",
            answer="Full refunds within 30 days. Partial refunds up to 90 days.",
            category="billing",
            keywords=["refund", "money back", "return"],
        ),
        FAQItem(
            id=4,
            question="How do I cancel my subscription?",
            answer="Go to Account > Subscriptions > Cancel. Your access continues until period end.",
            category="account",
            keywords=["cancel", "subscription", "unsubscribe"],
        ),
        FAQItem(
            id=5,
            question="Is my data secure?",
            answer="Yes, we use AES-256 encryption and are SOC 2 Type II certified.",
            category="security",
            keywords=["security", "encryption", "data", "privacy"],
        ),
        FAQItem(
            id=6,
            question="How do I enable two-factor authentication?",
            answer="Go to Settings > Security > Two-Factor Auth and scan the QR code.",
            category="security",
            keywords=["2fa", "two-factor", "authentication", "security"],
        ),
        FAQItem(
            id=7,
            question="Can I change my email address?",
            answer="Yes, go to Account > Profile > Email and verify the new address.",
            category="account",
            keywords=["email", "change", "update"],
        ),
        FAQItem(
            id=8,
            question="Why was my payment declined?",
            answer="Common reasons: expired card, insufficient funds, or bank block.",
            category="billing",
            keywords=["payment", "declined", "failed", "error"],
        ),
        FAQItem(
            id=9,
            question="How do I download my invoice?",
            answer="Go to Billing > History > select invoice > Download PDF.",
            category="billing",
            keywords=["invoice", "receipt", "download", "pdf"],
        ),
    ]


def exercise() -> None:
    """Run exercise tests."""
    print("Exercise 3: FAQ Hybrid Search System")
    print("=" * 50)

    # Create searcher and add FAQs
    faqs = create_sample_faqs()
    searcher = FAQSearcher()
    searcher.add_faqs(faqs)

    # Test 1: Basic search
    print("\nTest 1: Basic Search")
    print("-" * 40)
    query = "reset my password"
    results = searcher.search(query, top_k=3)

    print(f"Query: '{query}'")
    for r in results:
        print(f"  [{r.score:.3f}] {r.faq.question}")

    assert len(results) > 0, "Should return results"
    assert results[0].faq.id == 0, "Password reset FAQ should be first"
    print("PASSED!")

    # Test 2: Semantic search
    print("\nTest 2: Semantic Search")
    print("-" * 40)
    query = "how to make my account more secure"
    results = searcher.search(query, top_k=3)

    print(f"Query: '{query}'")
    for r in results:
        print(f"  [{r.score:.3f}] {r.faq.question}")

    # Should find security-related FAQs even without exact keyword match
    security_ids = {5, 6}  # Security FAQs
    result_ids = {r.faq.id for r in results}
    assert len(security_ids & result_ids) > 0, "Should find security FAQs semantically"
    print("PASSED!")

    # Test 3: Category filtering
    print("\nTest 3: Category Filtering")
    print("-" * 40)
    query = "payment"
    all_results = searcher.search(query, top_k=5)
    billing_results = searcher.search(query, top_k=5, category="billing")

    print(f"Query: '{query}'")
    print(f"All results: {len(all_results)}")
    print(f"Billing only: {len(billing_results)}")

    for r in billing_results:
        assert r.faq.category == "billing", f"Expected billing, got {r.faq.category}"
        print(f"  [{r.score:.3f}] [{r.faq.category}] {r.faq.question}")

    print("PASSED!")

    # Test 4: Related FAQs
    print("\nTest 4: Related FAQs")
    print("-" * 40)
    faq_id = 0  # Password reset
    related = searcher.get_related_faqs(faq_id, top_k=3)

    print(f"FAQs related to: '{faqs[faq_id].question}'")
    for r in related:
        print(f"  [{r.score:.3f}] {r.faq.question}")
        assert r.faq.id != faq_id, "Should not return the same FAQ"

    # Should find other account/security FAQs
    print("PASSED!")

    # Test 5: Verify hybrid behavior
    print("\nTest 5: Hybrid Ranking")
    print("-" * 40)
    query = "2FA security setup"
    results = searcher.search(query, top_k=3)

    print(f"Query: '{query}'")
    for r in results:
        print(f"  Score: {r.score:.3f}")
        print(f"  Vector rank: {r.vector_rank}, Keyword rank: {r.keyword_rank}")
        print(f"  FAQ: {r.faq.question}\n")

    print("PASSED!")

    print("\n" + "=" * 50)
    print("All tests passed! You've built a complete FAQ search system!")


if __name__ == "__main__":
    exercise()
