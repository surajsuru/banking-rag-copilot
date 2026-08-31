"""
chunker.py

Splits cleaned document text into meaningful chunks for vector embedding and retrieval.

Supported Strategies:
1. 'fixed': Fixed-size sliding window with character overlap.
2. 'heading_aware': Splits document along Markdown section headers (#, ##, ###)
   while preserving section context and header titles.
"""

import re
from typing import List, Dict, Any, Optional

from src.logger import get_logger

logger = get_logger(__name__)

# ── Default chunking parameters ───────────────────────────────────────────────
DEFAULT_CHUNK_SIZE = 500      # characters per chunk
DEFAULT_CHUNK_OVERLAP = 100   # character overlap


# ─────────────────────────────────────────────────────────────────────────────
# 1. FIXED-SIZE CHUNKING
# ─────────────────────────────────────────────────────────────────────────────

def chunk_text_fixed(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Splits text into overlapping fixed-size character chunks using a sliding window.
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
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# 2. HEADING-AWARE (STRUCTURE-AWARE) CHUNKING
# ─────────────────────────────────────────────────────────────────────────────

def chunk_text_heading_aware(
    text: str,
    max_chunk_size: int = 1000,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Splits text along Markdown headings (#, ##, ###, ####).
    Keeps related section content together. If an individual section exceeds
    max_chunk_size, it falls back to sliding window chunking for that section only.
    """
    if not text:
        return []

    # Regex matches Markdown headers (# Header 1, ## Header 2, etc.) at the start of a line
    header_pattern = r"(?m)^(#{1,4}\s+.+)$"
    sections = re.split(header_pattern, text)

    chunks: List[str] = []
    current_header = ""
    current_content = ""

    for item in sections:
        item = item.strip()
        if not item:
            continue

        # If the item is a header line (e.g. "## 2. RTGS Processing")
        if re.match(r"^#{1,4}\s+", item):
            # Flush existing accumulated section before starting a new one
            if current_content:
                full_section = f"{current_header}\n\n{current_content}".strip() if current_header else current_content
                if len(full_section) <= max_chunk_size:
                    chunks.append(full_section)
                else:
                    # Section is too long: sub-chunk it with fixed sliding window
                    sub_chunks = chunk_text_fixed(full_section, max_chunk_size, chunk_overlap)
                    chunks.extend(sub_chunks)

            current_header = item
            current_content = ""
        else:
            # It is section body content
            if current_content:
                current_content += "\n\n" + item
            else:
                current_content = item

    # Flush the last remaining section
    if current_content or current_header:
        full_section = f"{current_header}\n\n{current_content}".strip() if current_header else current_content
        if len(full_section) <= max_chunk_size:
            chunks.append(full_section)
        else:
            sub_chunks = chunk_text_fixed(full_section, max_chunk_size, chunk_overlap)
            chunks.extend(sub_chunks)

    # Fallback: if no markdown headers were detected, use fixed chunking
    if not chunks:
        chunks = chunk_text_fixed(text, max_chunk_size, chunk_overlap)

    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# 3. DOCUMENT-LEVEL CHUNKER INTERFACE
# ─────────────────────────────────────────────────────────────────────────────

def chunk_document(
    document: Dict[str, Any],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    strategy: str = "fixed",
) -> List[Dict[str, Any]]:
    """
    Takes a cleaned Document dict and returns a list of Chunk dicts with full metadata.

    Args:
        document:      Cleaned Document dictionary from cleaner.py.
        chunk_size:    Max characters per chunk.
        chunk_overlap: Character overlap between consecutive chunks.
        strategy:      'fixed' or 'heading_aware'.

    Returns:
        List of Chunk dicts containing content, positions, and lineage metadata.
    """
    text = document.get("text", "")

    if not text:
        logger.warning(f"Empty text in document: {document.get('file_name')}")
        return []

    # Select chunking strategy
    if strategy == "heading_aware":
        raw_chunks = chunk_text_heading_aware(text, max_chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif strategy == "fixed":
        raw_chunks = chunk_text_fixed(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    else:
        raise ValueError(f"Unknown chunking strategy '{strategy}'. Supported: 'fixed', 'heading_aware'")

    chunk_dicts = []
    start_char = 0

    for idx, chunk_content in enumerate(raw_chunks):
        end_char = start_char + len(chunk_content)

        chunk = {
            "text": chunk_content,
            "chunk_index": idx,
            "total_chunks": len(raw_chunks),
            "start_char": start_char,
            "end_char": end_char,
            "strategy": strategy,
            "source_file": document.get("file_name"),
            "source_path": document.get("file_path"),
            "extension": document.get("extension"),
            "metadata": dict(document.get("metadata", {})),
        }

        chunk_dicts.append(chunk)
        start_char += max(1, len(chunk_content) - chunk_overlap)

        logger.info(
        f"Chunked '{document.get('file_name')}' via [{strategy}] -> "
        f"{len(chunk_dicts)} chunks"
    )


    return chunk_dicts
