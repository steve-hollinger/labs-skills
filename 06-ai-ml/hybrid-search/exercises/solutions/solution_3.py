"""Solution for Exercise 3: Build a FAQ Hybrid Search System"""

from collections import defaultdict
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


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
        """Initialize the FAQ searcher."""
        self.model = SentenceTransformer(model_name)
        self.faqs: list[FAQItem] = []
        self.embeddings: NDArray[np.float32] | None = None
        self.bm25: BM25Okapi | None = None
        self.combined_texts: list[str] = []

    def add_faqs(self, faqs: list[FAQItem]) -> None:
        """Add FAQs to the search index."""
        self.faqs = faqs

        # Create combined text for each FAQ (question + answer + keywords)
        self.combined_texts = []
        for faq in faqs:
            combined = f"{faq.question} {faq.answer} {' '.join(faq.keywords)}"
            self.combined_texts.append(combined)

        # Generate embeddings
        self.embeddings = self.model.encode(
            self.combined_texts, convert_to_numpy=True
        )

        # Build BM25 index
        tokenized = [text.lower().split() for text in self.combined_texts]
        self.bm25 = BM25Okapi(tokenized)

    def _get_vector_ranking(self, query: str) -> list[int]:
        """Get FAQ IDs ranked by vector similarity."""
        if self.embeddings is None:
            return []

        # Encode query
        query_embedding = self.model.encode(query, convert_to_numpy=True)

        # Compute cosine similarity
        doc_norms = np.linalg.norm(self.embeddings, axis=1)
        query_norm = np.linalg.norm(query_embedding)

        similarities = np.dot(self.embeddings, query_embedding) / (
            doc_norms * query_norm + 1e-10
        )

        # Return indices sorted by similarity (descending)
        return np.argsort(similarities)[::-1].tolist()

    def _get_keyword_ranking(self, query: str) -> list[int]:
        """Get FAQ IDs ranked by BM25 score."""
        if self.bm25 is None:
            return []

        # Tokenize query
        tokenized_query = query.lower().split()

        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)

        # Return indices sorted by score (descending)
        return np.argsort(scores)[::-1].tolist()

    def _reciprocal_rank_fusion(
        self,
        vector_ranking: list[int],
        keyword_ranking: list[int],
        k: int = 60,
    ) -> list[tuple[int, float]]:
        """Combine rankings using RRF."""
        rrf_scores: dict[int, float] = defaultdict(float)

        # Create rank lookup for faster access
        vector_ranks = {doc_id: rank for rank, doc_id in enumerate(vector_ranking)}
        keyword_ranks = {doc_id: rank for rank, doc_id in enumerate(keyword_ranking)}

        # Compute RRF scores for all documents
        all_doc_ids = set(vector_ranking) | set(keyword_ranking)

        for doc_id in all_doc_ids:
            v_rank = vector_ranks.get(doc_id, len(vector_ranking))
            k_rank = keyword_ranks.get(doc_id, len(keyword_ranking))

            # RRF formula
            rrf_scores[doc_id] = 1 / (k + v_rank + 1) + 1 / (k + k_rank + 1)

        # Sort by RRF score descending
        return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    def search(
        self,
        query: str,
        top_k: int = 5,
        category: str | None = None,
    ) -> list[SearchResult]:
        """Search FAQs with hybrid ranking."""
        if not self.faqs:
            return []

        # Get rankings
        vector_ranking = self._get_vector_ranking(query)
        keyword_ranking = self._get_keyword_ranking(query)

        # Create rank lookups
        vector_ranks = {doc_id: rank for rank, doc_id in enumerate(vector_ranking)}
        keyword_ranks = {doc_id: rank for rank, doc_id in enumerate(keyword_ranking)}

        # Apply RRF fusion
        rrf_results = self._reciprocal_rank_fusion(vector_ranking, keyword_ranking)

        # Build results with optional category filtering
        results = []
        for doc_id, score in rrf_results:
            faq = self.faqs[doc_id]

            # Apply category filter
            if category is not None and faq.category != category:
                continue

            results.append(
                SearchResult(
                    faq=faq,
                    score=score,
                    vector_rank=vector_ranks.get(doc_id, -1),
                    keyword_rank=keyword_ranks.get(doc_id, -1),
                )
            )

            if len(results) >= top_k:
                break

        return results

    def get_related_faqs(self, faq_id: int, top_k: int = 3) -> list[SearchResult]:
        """Find FAQs related to a given FAQ."""
        if faq_id < 0 or faq_id >= len(self.faqs):
            return []

        # Use the FAQ's question as query
        faq = self.faqs[faq_id]
        query = faq.question

        # Search and filter out the original FAQ
        results = self.search(query, top_k=top_k + 1)
        return [r for r in results if r.faq.id != faq_id][:top_k]


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


def solution() -> None:
    """Run solution demonstration."""
    print("Solution 3: FAQ Hybrid Search System")
    print("=" * 50)

    # Create and populate searcher
    faqs = create_sample_faqs()
    searcher = FAQSearcher()
    searcher.add_faqs(faqs)

    print(f"\nIndexed {len(faqs)} FAQs")

    # Demonstrate various searches
    print("\n" + "-" * 50)
    print("Basic Search: 'reset my password'")
    print("-" * 50)
    results = searcher.search("reset my password", top_k=3)
    for r in results:
        print(f"  [{r.score:.4f}] (v:{r.vector_rank}, k:{r.keyword_rank})")
        print(f"    {r.faq.question}")

    print("\n" + "-" * 50)
    print("Semantic Search: 'how to make my account more secure'")
    print("-" * 50)
    results = searcher.search("how to make my account more secure", top_k=3)
    for r in results:
        print(f"  [{r.score:.4f}] (v:{r.vector_rank}, k:{r.keyword_rank})")
        print(f"    {r.faq.question}")

    print("\n" + "-" * 50)
    print("Category Filter: 'payment' (billing only)")
    print("-" * 50)
    results = searcher.search("payment", top_k=3, category="billing")
    for r in results:
        print(f"  [{r.score:.4f}] [{r.faq.category}] {r.faq.question}")

    print("\n" + "-" * 50)
    print("Related FAQs: to 'How do I reset my password?'")
    print("-" * 50)
    related = searcher.get_related_faqs(0, top_k=3)
    for r in related:
        print(f"  [{r.score:.4f}] {r.faq.question}")


if __name__ == "__main__":
    solution()
