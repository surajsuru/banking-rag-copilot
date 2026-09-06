"""
citations.py

Phase 7 - Citations & Grounding Engine.

Two responsibilities:
1. CitationExtractor  - Parses citation markers from the LLM answer into structured objects.
2. GroundingVerifier  - Computes a grounding score by checking how much of the LLM's
                        answer is actually backed by the retrieved document chunks.

Simple approach: No third-party libraries needed beyond what is already installed.
Uses token-level overlap (shared words / total unique words) as the grounding metric.
This is the same idea as the ROUGE-1 score used in NLP research.
"""

import re
from typing import List, Dict, Any, Tuple

from src.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# PART 1: CITATION EXTRACTOR
# ─────────────────────────────────────────────────────────────────────────────

# Matches patterns like:
#   [Source: imps_operations_guide.pdf (Chunk #1)]
#   [Source: transaction_reversal_sop.docx]
CITATION_PATTERN = re.compile(
    r"\[Source:\s*([^\]\(]+?)(?:\s*\(Chunk\s*#(\d+)\))?\]",
    re.IGNORECASE
)


def extract_citations(answer: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parses [Source: ...] markers from the LLM answer and links them
    back to the actual retrieved chunk objects.

    Args:
        answer: Raw text answer from the LLM.
        chunks: List of chunk dicts returned by VectorSearcher.

    Returns:
        List of citation dicts, each with:
        - 'source_file':      Filename of the cited document.
        - 'chunk_index':      Chunk position in document (or None).
        - 'chunk_id':         Full unique chunk ID (if matched to a retrieved chunk).
        - 'similarity_score': Similarity score of the chunk (if matched).
    """
    # Build lookup: (source_file, chunk_index) -> chunk
    chunk_lookup: Dict[Tuple[str, int], Dict] = {}
    for chunk in chunks:
        key = (chunk.get("source_file", ""), chunk.get("chunk_index", -1))
        chunk_lookup[key] = chunk

    seen = set()
    citations = []

    for match in CITATION_PATTERN.finditer(answer):
        source_file = match.group(1).strip()
        chunk_index = int(match.group(2)) if match.group(2) is not None else None

        # De-duplicate identical citations
        dedup_key = (source_file, chunk_index)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        # Try to link back to the original retrieved chunk
        matched_chunk = chunk_lookup.get((source_file, chunk_index), {})

        citations.append({
            "source_file":      source_file,
            "chunk_index":      chunk_index,
            "chunk_id":         matched_chunk.get("chunk_id", None),
            "similarity_score": matched_chunk.get("similarity", None),
        })

    logger.info(f"Extracted {len(citations)} unique citations from answer.")
    return citations


# ─────────────────────────────────────────────────────────────────────────────
# PART 2: GROUNDING VERIFIER
# ─────────────────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> set:
    """
    Converts text into a set of clean lowercase word tokens.
    Removes punctuation and stop words that carry no semantic meaning.

    Example: "The transaction limit is 1,000" -> {"transaction", "limit", "1000"}
    """
    STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can",
        "to", "of", "in", "on", "at", "by", "for", "with", "from",
        "and", "or", "but", "not", "if", "as", "this", "that", "it",
        "its", "their", "our", "your", "we", "you", "i", "they", "he",
        "she", "all", "any", "both", "each", "more", "most", "no",
        "only", "same", "than", "then", "there", "when", "where", "while",
    }
    # Remove punctuation, split on whitespace, lowercase, filter stop words
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in tokens if t not in STOP_WORDS and len(t) > 1}


def _sentence_overlap_score(sentence: str, context_tokens: set) -> float:
    """
    Computes Jaccard-style token overlap between a single sentence
    and the full pool of tokens from all retrieved chunks.

    Score = |sentence_tokens ∩ context_tokens| / |sentence_tokens|

    A score of 1.0 means every word in the sentence was found in the
    retrieved documents (fully grounded).
    A score of 0.0 means none of the words matched (potentially hallucinated).
    """
    sentence_tokens = _tokenize(sentence)
    if not sentence_tokens:
        return 1.0  # Empty / punctuation-only sentence: skip it

    overlap = sentence_tokens & context_tokens
    return len(overlap) / len(sentence_tokens)


def verify_grounding(
    answer: str,
    chunks: List[Dict[str, Any]],
    threshold: float = 0.55
) -> Dict[str, Any]:
    """
    Evaluates how well the LLM answer is grounded in the retrieved document chunks.

    Method:
    - Splits the answer into individual sentences.
    - For each sentence, computes the % of its words that exist in the retrieved chunks.
    - Sentences below the 'threshold' are flagged as "unsupported".
    - Overall grounding score is the average sentence score.

    Args:
        answer:    LLM-generated text answer.
        chunks:    Retrieved chunks from pgvector (the ground truth context).
        threshold: Sentences below this score are flagged as unsupported (default: 0.55).

    Returns:
        Dict with:
        - 'score':                 Float 0.0-1.0 (overall grounding level).
        - 'is_grounded':           True if score >= threshold.
        - 'unsupported_sentences': List of sentences that lacked document backing.
        - 'sentence_scores':       List of (sentence, score) tuples for every sentence.
    """
    if not answer or not chunks:
        return {
            "score": 0.0,
            "is_grounded": False,
            "unsupported_sentences": [answer] if answer else [],
            "sentence_scores": [],
        }

    # Build full context token pool from ALL retrieved chunks combined
    combined_context = " ".join(chunk.get("text", "") for chunk in chunks)
    context_tokens = _tokenize(combined_context)

    # Split answer into sentences (handles ., !, ?)
    sentences = [
        s.strip() for s in re.split(r"(?<=[.!?])\s+", answer)
        if s.strip() and len(s.strip()) > 15   # Ignore very short fragments
    ]

    if not sentences:
        return {
            "score": 1.0,
            "is_grounded": True,
            "unsupported_sentences": [],
            "sentence_scores": [],
        }

    sentence_scores = []
    unsupported = []

    for sentence in sentences:
        # Strip out citation markers before scoring (they are not content claims)
        clean_sentence = CITATION_PATTERN.sub("", sentence).strip()
        score = _sentence_overlap_score(clean_sentence, context_tokens)
        sentence_scores.append((sentence, round(score, 3)))

        if score < threshold:
            unsupported.append(sentence)

    overall_score = sum(s for _, s in sentence_scores) / len(sentence_scores)
    is_grounded = overall_score >= threshold

    logger.info(
        f"Grounding check: score={overall_score:.3f}, "
        f"grounded={is_grounded}, "
        f"unsupported_sentences={len(unsupported)}/{len(sentences)}"
    )

    return {
        "score":                 round(overall_score, 3),
        "is_grounded":           is_grounded,
        "unsupported_sentences": unsupported,
        "sentence_scores":       sentence_scores,
    }
