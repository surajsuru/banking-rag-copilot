from typing import List
from src.logger import get_logger

logger = get_logger(__name__)


def hit_rate(retrieved_sources: List[str], expected_sources: List[str]) -> float:
    """
    Checks if at least one expected source appears in the retrieved results.
    Returns 1.0 if any expected source was retrieved, 0.0 otherwise.
    """
    if not expected_sources:
        return 1.0  # abstain questions (Q010) have no expected source — treat as pass

    retrieved_basenames = {s.split("/")[-1] for s in retrieved_sources}
    expected_basenames  = {s.split("/")[-1] for s in expected_sources}

    return 1.0 if (retrieved_basenames & expected_basenames) else 0.0


def mean_reciprocal_rank(retrieved_sources: List[str], expected_sources: List[str]) -> float:
    """
    Reciprocal Rank of the first correctly retrieved source.
    Rank 1 = 1.0 | Rank 2 = 0.5 | Rank 3 = 0.33 | Not found = 0.0
    """
    if not expected_sources:
        return 1.0  # abstain case

    expected_basenames = {s.split("/")[-1] for s in expected_sources}

    for rank, source in enumerate(retrieved_sources, start=1):
        basename = source.split("/")[-1]
        if basename in expected_basenames:
            return 1.0 / rank  # ← reciprocal of position

    return 0.0  # expected doc never appeared


def precision_at_k(retrieved_sources: List[str], expected_sources: List[str], k: int) -> float:
    """
    Precision@K: fraction of the top-K retrieved sources that are relevant.

    Example:
        retrieved = ["error_code_reference.pdf", "sla_policy.md", "kyc_policy.pdf"]
        expected  = ["error_code_reference.pdf", "kyc_policy.pdf"]
        k=3  →  2 correct out of 3  →  0.667
    """
    if not expected_sources:
        return 1.0  # abstain case

    top_k = retrieved_sources[:k]

    retrieved_basenames = {s.split("/")[-1] for s in top_k}
    expected_basenames  = {s.split("/")[-1] for s in expected_sources}

    hits = len(retrieved_basenames & expected_basenames)
    return hits / k if k > 0 else 0.0

