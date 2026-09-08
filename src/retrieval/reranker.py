"""
reranker.py

Phase 9 - Cross-Encoder Reranker.

WHAT IS RERANKING?
After hybrid search returns the top-K candidate chunks, reranking
re-scores each candidate by reading the QUESTION and CHUNK TOGETHER.

WHY IS THIS MORE ACCURATE THAN VECTOR SEARCH?
- Vector search (bi-encoder): encodes query and chunk SEPARATELY,
  then compares them. Fast but less precise.
- Cross-encoder: reads query + chunk as ONE combined input.
  The model can see how words in the question relate to specific
  words in the chunk. Much more accurate but slower.

MODEL: cross-encoder/ms-marco-MiniLM-L-6-v2
- Trained on MS MARCO (Microsoft Machine Reading Comprehension dataset)
  with 8.8 million real-world query-passage relevance pairs.
- Output: a single float score (higher = more relevant)
- Size: ~66MB — fast enough to run on CPU at query time.

EXAMPLE:
  Query:  "What happens when IMPS reversal fails after debit?"
  Chunk:  "If the reversal cannot be completed after a confirmed debit,
           escalate immediately per SOP section 4.2"

  Cross-encoder reads both together and outputs: 0.94 (very relevant!)
  vs a generic IMPS overview chunk that scores: 0.21 (not relevant)
"""

from typing import List, Dict, Any

from sentence_transformers import CrossEncoder

from config import RERANKER_MODEL
from src.logger import get_logger

logger = get_logger(__name__)


class Reranker:
    """
    Re-scores retrieved chunks using a cross-encoder model.

    The cross-encoder reads (query, chunk_text) pairs and outputs
    a relevance score for each pair. Chunks are then re-sorted
    by this score for higher precision before passing to the LLM.

    Usage:
        reranker = Reranker()
        reranked = reranker.rerank(query, chunks, top_k=3)
    """

    def __init__(self, model_name: str = RERANKER_MODEL):
        """
        Loads the cross-encoder model.

        Args:
            model_name: HuggingFace model identifier for the cross-encoder.
                        Defaults to RERANKER_MODEL from config.py.
        """
        logger.info(f"Loading cross-encoder reranker: '{model_name}'...")
        self.model = CrossEncoder(model_name)
        logger.info(f"Reranker '{model_name}' loaded successfully.")

    def rerank(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Re-scores and re-sorts candidate chunks by cross-encoder relevance.

        Process:
        1. Build (query, chunk_text) pairs for every candidate chunk.
        2. Pass ALL pairs through the cross-encoder in one batch.
        3. Attach the score to each chunk.
        4. Sort by score descending (most relevant first).
        5. Return top_k results.

        Args:
            query:   The user's original question.
            chunks:  Candidate chunks from hybrid search (pre-filtered).
            top_k:   How many top-scored chunks to return after reranking.

        Returns:
            List of top_k chunk dicts sorted by 'rerank_score' descending.
            Each chunk has a new 'rerank_score' field added.
        """
        if not chunks:
            logger.warning("Reranker received empty chunk list - skipping.")
            return []

        # Build input pairs: [(query, chunk1_text), (query, chunk2_text), ...]
        # The cross-encoder needs the question and the passage together
        pairs = [(query, chunk.get("text", "")) for chunk in chunks]

        # Score all pairs in one batch (efficient - single model forward pass)
        scores = self.model.predict(pairs)

        # Attach the rerank score to each chunk
        scored_chunks = []
        for chunk, score in zip(chunks, scores):
            enriched = chunk.copy()
            enriched["rerank_score"] = round(float(score), 4)
            scored_chunks.append(enriched)

        # Sort by rerank_score descending (highest relevance first)
        scored_chunks.sort(key=lambda x: x["rerank_score"], reverse=True)

        # Return only top_k
        results = scored_chunks[:top_k]

        top_score = results[0]["rerank_score"] if results else 0.0
        logger.info(
            f"Reranking complete: {len(chunks)} candidates -> "
            f"{len(results)} results (top score: {top_score:.4f})"
        )

        return results
