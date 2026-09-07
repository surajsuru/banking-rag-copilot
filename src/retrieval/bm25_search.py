"""
bm25_search.py

Phase 8 - BM25 Keyword Search Engine.

BM25 (Best Match 25) is a classic keyword-based ranking algorithm used by
Elasticsearch, Apache Lucene, and most enterprise search engines.

WHY BM25 alongside vector search?
- Vector search finds semantically SIMILAR text (meaning-based).
- BM25 finds EXACT keyword matches (term-based).
- Banking documents contain specific codes like "TXN-1002", "IMPS_FAILED",
  "RBI-2024-01" that vector search can miss if they are rare in the embedding
  model's training data. BM25 catches these exact matches reliably.

HOW BM25 WORKS (simple explanation):
- Treats each chunk as a "bag of words".
- Scores each chunk based on:
  1. Term Frequency  (TF)  - How often the query word appears in the chunk.
  2. Inverse Document Frequency (IDF) - How rare the word is across all chunks.
     (rare words like "IMPS_FAILED" score higher than common words like "the")
  3. Document Length normalization - Longer chunks don't get unfair advantage.
"""

import re
from typing import List, Dict, Any

from rank_bm25 import BM25Okapi

from src.logger import get_logger

logger = get_logger(__name__)


def _tokenize(text: str) -> List[str]:
    """
    Converts raw text into a list of clean lowercase tokens for BM25 indexing.

    Example:
        "IMPS_FAILED: Terminal failure in TXN-1002"
        -> ["imps", "failed", "terminal", "failure", "txn", "1002"]

    Note: We split on non-alphanumeric characters so that codes like
    "TXN-1002" become ["txn", "1002"] - both parts become searchable.
    """
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25Searcher:
    """
    Keyword-based search over all document chunks using the BM25Okapi algorithm.

    Usage:
        searcher = BM25Searcher(chunks)
        results  = searcher.search("IMPS_FAILED terminal failure", top_k=3)
    """

    def __init__(self, chunks: List[Dict[str, Any]]):
        """
        Builds the BM25 index from the provided list of chunk dictionaries.

        Args:
            chunks: List of chunk dicts, each must have at least a 'text' key.
                    These are the same chunk objects stored in PostgreSQL.
        """
        self.chunks = chunks

        if not chunks:
            logger.warning("BM25Searcher initialized with zero chunks - index is empty.")
            self.bm25 = None
            return

        # Tokenize every chunk's text to build the BM25 corpus
        # corpus = [["imps", "failed", "terminal", ...], ["upi", "payment", ...], ...]
        corpus = [_tokenize(chunk.get("text", "")) for chunk in chunks]

        # Build the BM25 index from the tokenized corpus
        self.bm25 = BM25Okapi(corpus)

        logger.info(f"BM25 index built with {len(chunks)} chunks.")

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Searches the BM25 index for chunks most relevant to the query.

        Args:
            query: The user's question or search string.
            top_k: Number of top results to return.

        Returns:
            List of chunk dicts, each enriched with a 'bm25_score' field.
            Sorted by BM25 score descending (best match first).
        """
        if self.bm25 is None or not self.chunks:
            logger.warning("BM25 search called on empty index - returning no results.")
            return []

        # Tokenize the query the same way we tokenized the corpus
        query_tokens = _tokenize(query)

        if not query_tokens:
            logger.warning("BM25 query produced zero tokens after tokenization.")
            return []

        # Get BM25 scores for every chunk in the corpus
        # scores[i] = BM25 relevance score of chunk i for this query
        scores = self.bm25.get_scores(query_tokens)

        # Pair each chunk with its BM25 score and sort descending
        scored_chunks = [
            {**chunk, "bm25_score": float(scores[i])}
            for i, chunk in enumerate(self.chunks)
        ]
        scored_chunks.sort(key=lambda x: x["bm25_score"], reverse=True)

        # Return only the top-K results
        results = scored_chunks[:top_k]

        top_score = results[0]["bm25_score"] if results else 0.0
        logger.info(
            f"BM25 search for '{query[:60]}' -> {len(results)} results "
            f"(top score: {top_score:.4f})"
        )

        return results
