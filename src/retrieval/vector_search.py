"""
vector_search.py

Performs semantic retrieval against PostgreSQL + pgvector.
Takes a natural language user query, converts it into a dense vector,
and retrieves the top-K most semantically similar document chunks.
"""

from typing import List, Dict, Any, Optional

from src.logger import get_logger
from src.embeddings.embedder import Embedder
from src.database.vector_store import connect, search

logger = get_logger(__name__)


class VectorSearcher:
    """
    Handles end-to-end semantic vector search:
    Query String -> Dense Vector Embedding -> PostgreSQL pgvector ANN search -> Ranked Results
    """

    def __init__(self, embedder: Optional[Embedder] = None, top_k: int = 3, min_similarity: float = 0.0):
        """
        Args:
            embedder: Pre-initialized Embedder instance (creates a new one if None).
            top_k: Default number of top results to retrieve.
            min_similarity: Threshold score (0.0 to 1.0) below which chunks are discarded.
        """
        self.embedder = embedder or Embedder()
        self.top_k = top_k
        self.min_similarity = min_similarity
        self._conn = None

    @property
    def conn(self):
        """Lazy database connection manager."""
        if self._conn is None or self._conn.closed:
            self._conn = connect()
        return self._conn

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieves top_k most similar chunks for a given natural language query.

        Args:
            query: The user question or search phrase.
            top_k: Number of chunks to retrieve (defaults to self.top_k).

        Returns:
            List of dictionaries with keys:
            - 'chunk_id': unique identifier
            - 'text': chunk text content
            - 'source_file': original document filename
            - 'chunk_index': chunk position in document
            - 'similarity': float between 0.0 and 1.0 (higher is better)
        """
        if not query or not query.strip():
            logger.warning("Empty query provided to VectorSearcher.")
            return []

        k = top_k or self.top_k
        logger.info(f"Searching for: '{query}' (top_k={k})")

        # 1. Convert user text query into a 384-dimensional vector
        query_vector = self.embedder.embed_text(query)

        # 2. Query pgvector using cosine distance
        raw_results = search(self.conn, query_vector, top_k=k)

        # 3. Filter by minimum similarity threshold if configured
        filtered_results = [
            res for res in raw_results if res["similarity"] >= self.min_similarity
        ]

        logger.info(f"Retrieved {len(filtered_results)} relevant chunks (top score: {filtered_results[0]['similarity'] if filtered_results else 'N/A'})")
        return filtered_results

    def close(self):
        """Closes the underlying database connection."""
        if self._conn and not self._conn.closed:
            self._conn.close()
            logger.info("VectorSearcher database connection closed.")
