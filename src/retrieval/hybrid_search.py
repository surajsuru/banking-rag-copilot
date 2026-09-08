"""
hybrid_search.py

Phase 8 - Hybrid Search Engine (BM25 + Vector Search).

Combines two retrieval methods into one final ranked list:
  1. Vector Search   -> Finds semantically SIMILAR chunks (meaning-based)
  2. BM25 Search     -> Finds EXACT keyword matches (term-based)

WHY HYBRID?
- Vector search alone misses exact codes like "TXN-1002", "IMPS_FAILED"
- BM25 alone misses paraphrased or semantically related content
- Combining both gives the best of both worlds

FUSION ALGORITHM: Reciprocal Rank Fusion (RRF)
- Each chunk gets a score from BOTH ranked lists
- RRF formula: score = 1 / (rank + K) where K=60 (a smoothing constant)
- Final scores from both lists are ADDED together
- Chunks that appear high in BOTH lists score highest
- Chunks that appear in only one list still get a partial score

Example:
  Vector rank 1  -> RRF score = 1/(1+60)  = 0.0164
  BM25   rank 1  -> RRF score = 1/(1+60)  = 0.0164
  Combined score -> 0.0164 + 0.0164 = 0.0328  (strong signal from both)

  Vector rank 1  -> RRF score = 0.0164
  BM25   rank 50 -> RRF score = 1/(50+60) = 0.0091
  Combined score -> 0.0164 + 0.0091 = 0.0255  (good, but not in both top lists)
"""

from typing import List, Dict, Any

from src.retrieval.vector_search import VectorSearcher
from src.retrieval.bm25_search import BM25Searcher
from src.retrieval.reranker import Reranker
from src.logger import get_logger

logger = get_logger(__name__)

# RRF smoothing constant - 60 is the standard value from the original RRF paper
RRF_K = 60


def _reciprocal_rank_fusion(
    vector_results: List[Dict[str, Any]],
    bm25_results: List[Dict[str, Any]],
    top_k: int
) -> List[Dict[str, Any]]:
    """
    Merges two ranked result lists using Reciprocal Rank Fusion (RRF).

    Args:
        vector_results: Chunks ranked by vector similarity (best first).
        bm25_results:   Chunks ranked by BM25 keyword score (best first).
        top_k:          How many final results to return.

    Returns:
        Merged and re-ranked list of chunk dicts with 'rrf_score' field added.
        Sorted by rrf_score descending.
    """
    # Dictionary to accumulate RRF scores: chunk_id -> total_rrf_score
    rrf_scores: Dict[str, float] = {}

    # Dictionary to store the full chunk object by chunk_id
    chunk_map: Dict[str, Dict[str, Any]] = {}

    # --- Process Vector Search results ---
    # rank starts at 1 (position 1 = best match)
    for rank, chunk in enumerate(vector_results, start=1):
        chunk_id = chunk.get("chunk_id", chunk.get("text", "")[:50])
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + 1.0 / (rank + RRF_K)
        chunk_map[chunk_id] = chunk

    # --- Process BM25 results ---
    for rank, chunk in enumerate(bm25_results, start=1):
        chunk_id = chunk.get("chunk_id", chunk.get("text", "")[:50])
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + 1.0 / (rank + RRF_K)
        # Only update chunk_map if not already present (vector result takes priority)
        if chunk_id not in chunk_map:
            chunk_map[chunk_id] = chunk

    # Sort all unique chunks by their combined RRF score (highest first)
    sorted_ids = sorted(rrf_scores, key=lambda cid: rrf_scores[cid], reverse=True)

    # Build final result list with rrf_score attached
    final_results = []
    for chunk_id in sorted_ids[:top_k]:
        chunk = chunk_map[chunk_id].copy()
        chunk["rrf_score"] = round(rrf_scores[chunk_id], 6)
        final_results.append(chunk)

    return final_results


class HybridSearcher:
    """
    Combines VectorSearcher (semantic) and BM25Searcher (keyword) into one
    unified search interface using Reciprocal Rank Fusion.

    Usage:
        searcher = HybridSearcher(top_k=5)
        results  = searcher.search("What is error code TXN-1002?")
        searcher.close()
    """

    def __init__(self, top_k: int = 5):
        """
        Initializes the hybrid searcher.
        Loads all chunks from PostgreSQL for BM25 indexing.

        Args:
            top_k: Number of final merged results to return.
        """
        self.top_k = top_k

        # Vector searcher: handles PostgreSQL connection and pgvector queries
        self.vector_searcher = VectorSearcher()

        # Load ALL chunks from the database to build the in-memory BM25 index
        # BM25 needs all documents upfront to calculate IDF (rarity scores)
        all_chunks = self._load_all_chunks()
        self.bm25_searcher = BM25Searcher(all_chunks)
        self.reranker = Reranker()


        logger.info(
            f"HybridSearcher initialized: "
            f"{len(all_chunks)} chunks in BM25 index, top_k={top_k}"
        )

    def _load_all_chunks(self) -> List[Dict[str, Any]]:
        """
        Fetches all text chunks from PostgreSQL for BM25 index construction.

        Returns:
            List of all chunk dicts from the database.
        """
        conn = self.vector_searcher.conn
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT chunk_id, text, source_file, chunk_index FROM chunks ORDER BY chunk_id"
            )
            rows = cursor.fetchall()

        chunks = [
            {
                "chunk_id":    row[0],
                "text":        row[1],
                "source_file": row[2],
                "chunk_index": row[3],
            }
            for row in rows
        ]

        logger.info(f"Loaded {len(chunks)} chunks from database for BM25 index.")
        return chunks

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Runs both vector and BM25 search, then fuses results using RRF.

        Args:
            query: The user's natural language question.

        Returns:
            Top-K chunks ranked by combined RRF score.
            Each chunk dict includes:
            - All standard chunk fields (chunk_id, text, source_file, etc.)
            - 'rrf_score':    Combined RRF fusion score
            - 'similarity':   Cosine similarity from vector search (if applicable)
            - 'bm25_score':   BM25 keyword score (if applicable)
        """
        logger.info(f"Hybrid search for: '{query[:80]}' (top_k={self.top_k})")

        # Fetch more candidates than top_k from each method for better fusion coverage
        candidate_k = max(self.top_k * 3, 10)

        # --- Run Vector Search ---
        vector_results = self.vector_searcher.search(query, top_k=candidate_k)
        logger.info(f"Vector search returned {len(vector_results)} candidates.")

        # --- Run BM25 Search ---
        bm25_results = self.bm25_searcher.search(query, top_k=candidate_k)
        logger.info(f"BM25 search returned {len(bm25_results)} candidates.")

        # --- Fuse with RRF ---
        final_results = _reciprocal_rank_fusion(
            vector_results, bm25_results, top_k=self.top_k
        )

        # --- Rerank with cross-encoder for higher precision ---
        final_results = self.reranker.rerank(query, final_results, top_k=self.top_k)

        top_score = final_results[0]["rrf_score"] if final_results else 0.0
        logger.info(
            f"Hybrid Search complete: {len(final_results)} results "
            f"(top RRF score: {top_score:.6f})"
        )

        return final_results

    def close(self):
        """Closes the database connection held by the vector searcher."""
        if self.vector_searcher:
            self.vector_searcher.close()
            logger.info("HybridSearcher database connection closed.")


# ─────────────────────────────────────────────────────────────────────────────
# Quick test when run directly
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

    searcher = HybridSearcher(top_k=3)

    test_query = "What is the procedure to reverse a failed IMPS transaction?"
    print(f"\n{'='*70}")
    print(f"HYBRID SEARCH: {test_query}")
    print(f"{'='*70}")

    results = searcher.search(test_query)

    for i, chunk in enumerate(results, 1):
        print(f"\n[Result {i}]")
        print(f"  Source:     {chunk.get('source_file')} (Chunk #{chunk.get('chunk_index')})")
        print(f"  RRF Score:  {chunk.get('rrf_score')}")
        print(f"  Similarity: {chunk.get('similarity', 'N/A')}")
        print(f"  BM25 Score: {chunk.get('bm25_score', 'N/A')}")
        print(f"  Text:       {chunk.get('text', '')[:150]}...")

    print(f"\n{'='*70}")
    searcher.close()
