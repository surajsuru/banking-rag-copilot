"""
prompt.py

Constructs structured prompts for the LLM.
Formats retrieved document chunks into clean context blocks and enforces
strict banking compliance and anti-hallucination instructions.
"""

from typing import List, Dict, Any
from config import MAX_CONTEXT_CHARS
from src.logger import get_logger

logger = get_logger(__name__)


# System prompt defining the AI persona and strict operational guardrails
BANKING_SYSTEM_PROMPT = """You are an expert AI Banking Operations Copilot for internal bank staff.
Your role is to answer questions about banking procedures, payment processing (UPI, NEFT, RTGS, IMPS),
reconciliation, API specifications, compliance, and error codes.

CRITICAL OPERATIONAL RULES:
1. Answer ONLY using the facts directly mentioned in the provided Context below.
2. If the answer cannot be determined from the Context, reply EXACTLY:
   "I do not have sufficient information in the banking documentation to answer this question."
3. Do NOT assume, extrapolate, or invent policies, limits, fees, or turnaround times (TAT).
4. Always cite the relevant document source(s) using format: [Source: filename.ext].
5. Keep your answers concise, professional, and well-structured using bullet points where appropriate.
"""


def format_context(chunks: List[Dict[str, Any]], max_chars: int = MAX_CONTEXT_CHARS) -> str:
    """
    Formats retrieved chunks into a context block for the LLM.
    Respects a character budget to control token cost.

    Args:
        chunks:    Retrieved chunk dicts, already sorted by relevance.
        max_chars: Maximum total characters allowed in context (~tokens * 4).

    Returns:
        Formatted context string, truncated to max_chars budget.
    """
    if not chunks:
        return "No relevant documentation found."

    context_parts = []
    total_chars   = 0

    for i, chunk in enumerate(chunks, 1):
        source    = chunk.get("source_file", "unknown_document")
        chunk_idx = chunk.get("chunk_index", 0)
        text      = chunk.get("text", "").strip()

        block = f"--- [Document {i}] Source: {source} (Chunk #{chunk_idx}) ---\n{text}"

        # Stop adding chunks if we'd exceed the character budget
        if total_chars + len(block) > max_chars:
            logger.warning(
                f"Context budget hit at chunk {i}/{len(chunks)} "
                f"({total_chars} chars used / {max_chars} allowed). "
                f"Remaining {len(chunks) - i + 1} chunk(s) dropped."
            )
            break

        context_parts.append(block)
        total_chars += len(block)

    return "\n\n".join(context_parts)


def build_prompt(query: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Builds the standard chat messages list (compatible with Groq / OpenAI / Ollama).

    Args:
        query: The user's question.
        chunks: List of retrieved chunk dictionaries from VectorSearcher.

    Returns:
        List of message dicts:
        [
            {"role": "system", "content": BANKING_SYSTEM_PROMPT},
            {"role": "user", "content": "...context + query..."}
        ]
    """
    formatted_context = format_context(chunks)

    user_content = f"""CONTEXT FROM BANKING KNOWLEDGE BASE:
{formatted_context}

USER QUESTION:
{query}

ANSWER (Grounded strictly in the context above):"""

    return [
        {"role": "system", "content": BANKING_SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]
