"""
chunker.py

Splits cleaned document text into overlapping chunks.
Chunks are the fundamental unit of retrieval in a RAG system.

Strategy implemented here: Fixed-size character chunking with overlap.
This is the simplest and most universally applicable strategy.
Later phases will add: token-based chunking, heading-aware chunking.
"""

from typing import List, Dict, Any

from src.logger import get_logger

logger = get_logger(__name__)

# ── Default chunking parameters ───────────────────────────────────────────────
# These are starting defaults. You will experiment with these values
# in Phase 4 (Chunking Benchmark) to understand how they affect retrieval.
DEFAULT_CHUNK_SIZE    = 500   # characters per chunk
DEFAULT_CHUNK_OVERLAP = 100   # characters repeated between adjacent chunks


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Splits text into overlapping fixed-size character chunks.

    Args:
        text:          The cleaned text to split.
        chunk_size:    Maximum number of characters per chunk.
        chunk_overlap: Number of characters to repeat between adjacent chunks.

    Returns:
        A list of text chunk strings.
    """
    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})"
        )

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        # Extract the chunk (Python slicing handles end > len safely)
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        # Move start forward by (chunk_size - overlap)
        # This is what creates the sliding window with overlap
        start += chunk_size - chunk_overlap

    return chunks


def chunk_document(
    document: Dict[str, Any],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Takes a cleaned Document dict and returns a list of Chunk dicts.

    Each chunk carries forward the parent document's metadata
    plus its own position information (chunk_index, start_char, end_char).

    This metadata is critical later for:
    - Citations (which document + position)
    - Access control (inherit parent document's permissions)
    - Deduplication
    - Debugging retrieval failures

    Args:
        document:      A cleaned Document dict from cleaner.py
        chunk_size:    Characters per chunk
        chunk_overlap: Overlap between adjacent chunks

    Returns:
        List of Chunk dicts, each representing one retrievable unit.
    """
    text = document.get("text", "")

    if not text:
        logger.warning(f"Empty text in document: {document.get('file_name')}")
        return []

    raw_chunks = chunk_text(text, chunk_size, chunk_overlap)

    chunk_dicts = []
    start_char = 0

    for idx, chunk_text_content in enumerate(raw_chunks):
        end_char = start_char + len(chunk_text_content)

        chunk = {
            # ── Content ───────────────────────────────────────────
            "text": chunk_text_content,

            # ── Position within parent document ───────────────────
            "chunk_index":  idx,               # 0-based position
            "total_chunks": len(raw_chunks),   # total chunks from this doc
            "start_char":   start_char,        # character offset in original text
            "end_char":     end_char,          # end character offset

            # ── Parent document identity (for citations) ──────────
            "source_file":  document.get("file_name"),
            "source_path":  document.get("file_path"),
            "extension":    document.get("extension"),

            # ── Inherited metadata ────────────────────────────────
            "metadata": dict(document.get("metadata", {})),
        }

        chunk_dicts.append(chunk)

        # Advance start by chunk_size minus overlap
        start_char += chunk_size - chunk_overlap

    logger.info(
        f"Chunked '{document.get('file_name')}' → "
        f"{len(chunk_dicts)} chunks "
        f"(size={chunk_size}, overlap={chunk_overlap})"
    )

    return chunk_dicts
