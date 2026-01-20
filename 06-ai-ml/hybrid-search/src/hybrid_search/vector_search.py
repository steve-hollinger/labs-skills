"""Vector similarity search using sentence-transformers."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer


@dataclass
class VectorSearchResult:
    """Result from vector similarity search."""

    doc_id: int
    score: float
    document: str


class VectorSearcher:
    """Vector similarity search using sentence-transformers embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initialize the vector searcher.

        Args:
            model_name: Name of the sentence-transformer model to use.
                       Common options:
                       - all-MiniLM-L6-v2: Fast, good quality (384 dims)
                       - all-mpnet-base-v2: Better quality (768 dims)
                       - e5-large-v2: Best quality (1024 dims)
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.documents: list[str] = []
        self.embeddings: NDArray[np.float32] | None = None

    def index(self, documents: list[str], show_progress: bool = False) -> None:
        """Index documents by computing their embeddings.

        Args:
            documents: List of documents to index.
            show_progress: Whether to show a progress bar.
        """
        self.documents = documents
        if documents:
            self.embeddings = self.model.encode(
                documents,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
            )
        else:
            self.embeddings = None

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[VectorSearchResult]:
        """Search for documents similar to the query.

        Args:
            query: The search query.
            top_k: Number of results to return.

        Returns:
            List of search results sorted by similarity (highest first).
        """
        if not self.documents or self.embeddings is None:
            return []

        # Encode query
        query_embedding = self.model.encode(query, convert_to_numpy=True)

        # Compute cosine similarity
        scores = self._cosine_similarity(query_embedding)

        # Get top-k indices
        top_k = min(top_k, len(self.documents))
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [
            VectorSearchResult(
                doc_id=int(idx),
                score=float(scores[idx]),
                document=self.documents[idx],
            )
            for idx in top_indices
        ]

    def get_scores(self, query: str) -> NDArray[np.float32]:
        """Get similarity scores for all documents.

        Args:
            query: The search query.

        Returns:
            Array of similarity scores for each document.
        """
        if not self.documents or self.embeddings is None:
            return np.array([], dtype=np.float32)

        query_embedding = self.model.encode(query, convert_to_numpy=True)
        return self._cosine_similarity(query_embedding)

    def _cosine_similarity(
        self, query_embedding: NDArray[np.float32]
    ) -> NDArray[np.float32]:
        """Compute cosine similarity between query and all documents."""
        if self.embeddings is None:
            return np.array([], dtype=np.float32)

        # Normalize embeddings
        doc_norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        query_norm = np.linalg.norm(query_embedding)

        # Avoid division by zero
        doc_norms = np.maximum(doc_norms, 1e-10)
        query_norm = max(query_norm, 1e-10)

        # Compute cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            doc_norms.flatten() * query_norm
        )

        return similarities.astype(np.float32)

    def get_ranking(self, query: str) -> list[int]:
        """Get document IDs ranked by similarity.

        Args:
            query: The search query.

        Returns:
            List of document IDs sorted by similarity (highest first).
        """
        scores = self.get_scores(query)
        if len(scores) == 0:
            return []
        return np.argsort(scores)[::-1].tolist()
