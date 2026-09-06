"""
prompt.py

Constructs structured prompts for the LLM.
Formats retrieved document chunks into clean context blocks and enforces
strict banking compliance and anti-hallucination instructions.
"""

from typing import List, Dict, Any

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


def format_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Formats a list of retrieved chunks into a clear, delimited context block for the LLM.

    Example output:
    ---
    [Document 1] Source: transaction_reversal_sop.docx (Chunk #0)
    Transaction Reversal Standard Operating Procedure...
    ---
    """
    if not chunks:
        return "No relevant documentation found."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source_file", "unknown_document")
        chunk_idx = chunk.get("chunk_index", 0)
        text = chunk.get("text", "").strip()

        context_parts.append(
            f"--- [Document {i}] Source: {source} (Chunk #{chunk_idx}) ---\n{text}"
        )

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
