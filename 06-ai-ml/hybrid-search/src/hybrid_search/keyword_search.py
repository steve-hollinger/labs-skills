"""BM25 keyword search implementation."""

import re
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from rank_bm25 import BM25Okapi


@dataclass
class KeywordSearchResult:
    """Result from keyword search."""

    doc_id: int
    score: float
    document: str


def simple_tokenize(text: str) -> list[str]:
    """Simple tokenization: lowercase and split on non-alphanumeric.

    Args:
        text: Text to tokenize.

    Returns:
        List of tokens.
    """
    # Convert to lowercase and split on non-alphanumeric characters
    tokens = re.findall(r"\b\w+\b", text.lower())
    return tokens


class BM25Searcher:
    """BM25 keyword search using rank-bm25."""

    def __init__(
        self,
        tokenizer: callable = simple_tokenize,  # type: ignore[type-arg]
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        """Initialize the BM25 searcher.

        Args:
            tokenizer: Function to tokenize text. Default splits on whitespace.
            k1: BM25 term frequency saturation parameter (typical: 1.2-2.0).
            b: BM25 length normalization parameter (typical: 0.75).
        """
        self.tokenizer = tokenizer
        self.k1 = k1
        self.b = b
        self.documents: list[str] = []
        self.tokenized_docs: list[list[str]] = []
        self.bm25: BM25Okapi | None = None

    def index(self, documents: list[str]) -> None:
        """Index documents for BM25 search.

        Args:
            documents: List of documents to index.
        """
        self.documents = documents
        self.tokenized_docs = [self.tokenizer(doc) for doc in documents]

        if documents:
            self.bm25 = BM25Okapi(
                self.tokenized_docs,
                k1=self.k1,
                b=self.b,
            )
        else:
            self.bm25 = None

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[KeywordSearchResult]:
        """Search for documents matching the query.

        Args:
            query: The search query.
            top_k: Number of results to return.

        Returns:
            List of search results sorted by BM25 score (highest first).
        """
        if not self.documents or self.bm25 is None:
            return []

        # Tokenize query
        tokenized_query = self.tokenizer(query)

        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices
        top_k = min(top_k, len(self.documents))
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [
            KeywordSearchResult(
                doc_id=int(idx),
                score=float(scores[idx]),
                document=self.documents[idx],
            )
            for idx in top_indices
        ]

    def get_scores(self, query: str) -> NDArray[np.float64]:
        """Get BM25 scores for all documents.

        Args:
            query: The search query.

        Returns:
            Array of BM25 scores for each document.
        """
        if not self.documents or self.bm25 is None:
            return np.array([], dtype=np.float64)

        tokenized_query = self.tokenizer(query)
        scores = self.bm25.get_scores(tokenized_query)
        return np.array(scores, dtype=np.float64)

    def get_ranking(self, query: str) -> list[int]:
        """Get document IDs ranked by BM25 score.

        Args:
            query: The search query.

        Returns:
            List of document IDs sorted by score (highest first).
        """
        scores = self.get_scores(query)
        if len(scores) == 0:
            return []
        return np.argsort(scores)[::-1].tolist()
