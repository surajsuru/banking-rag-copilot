"""
cleaner.py

Sanitizes, normalizes, and cleans extracted text from raw documents.
Ensures consistent formatting, whitespace handling, and unicode normalization.
"""

import re
import unicodedata
from typing import Dict, Any

from src.logger import get_logger

logger = get_logger(__name__)


def clean_text(text: str) -> str:
    """
    Cleans and normalizes text content:
    1. Unicode NFKC normalization (turns special/weird chars into standard equivalents)
    2. Replaces non-breaking spaces and zero-width spaces
    3. Normalizes line breaks to '\n'
    4. Strips trailing whitespace from each line
    5. Collapses 3 or more consecutive newlines into 2
    6. Collapses multiple spaces/tabs within lines into a single space
    """
    if not text:
        return ""

    # 1. Unicode normalization (NFKC decomposes and recomposes characters to standard forms)
    text = unicodedata.normalize("NFKC", text)

    # 2. Replace weird space characters
    text = text.replace("\xa0", " ")
    text = text.replace("\u200b", "")  # zero-width space
    text = text.replace("\ufeff", "")  # byte order mark (BOM)

    # 3. Normalize CRLF to LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 4. Clean each line: collapse internal spaces/tabs, strip leading/trailing spaces
    lines = []
    for line in text.split("\n"):
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(cleaned_line)
    text = "\n".join(lines)

    # 5. Collapse 3+ newlines into 2 (preserve paragraph separation without empty gaps)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def clean_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes a Document dict from parser.py, cleans its 'text' field,
    and adds cleaning statistics to the metadata.
    """
    original_len = len(document.get("text", ""))
    cleaned = clean_text(document.get("text", ""))
    cleaned_len = len(cleaned)

    # Clone document dict and update text
    cleaned_doc = dict(document)
    cleaned_doc["text"] = cleaned
    
    # Store cleaning stats in metadata
    metadata = dict(cleaned_doc.get("metadata", {}))
    metadata["raw_char_count"] = original_len
    metadata["cleaned_char_count"] = cleaned_len
    metadata["chars_removed"] = original_len - cleaned_len
    cleaned_doc["metadata"] = metadata

    return cleaned_doc
