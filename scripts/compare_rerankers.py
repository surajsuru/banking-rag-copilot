"""
compare_rerankers.py

A/B Comparison Script: CrossEncoder vs JEVReranker
----------------------------------------------------
Runs both rerankers on the same retrieved candidates for each eval question
and compares them on:
  - MRR  (Mean Reciprocal Rank) -- where does the correct chunk land?
  - Top-1 Hit Rate              -- is the best chunk ranked #1?
  - Avg Rerank Score            -- overall confidence of the reranker
  - Latency per query           -- JEV is API-based, cross-encoder is local

Usage:
    python scripts/compare_rerankers.py

Decision rule:
    If JEV MRR > CrossEncoder MRR --> set JEV_RERANKER_ENABLED=true in .env
"""

import sys
import time
from pathlib import Path
import time


# Add project root to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.retrieval.hybrid_search import HybridSearcher
from src.retrieval.reranker import Reranker, JEVReranker
from src.evaluation.dataset import load_dataset
from src.logger import get_logger

logger = get_logger(__name__)

# Config
TOP_K        = 5     # Candidates to retrieve before reranking
RERANK_TOP_K = 3     # Final chunks after reranking
ROLE         = "admin"


def reciprocal_rank(chunks: list, expected_sources: list) -> float:
    for rank, chunk in enumerate(chunks, start=1):
        if chunk.get("source_file", "") in expected_sources:
            return 1.0 / rank
    return 0.0


def top1_hit(chunks: list, expected_sources: list) -> bool:
    if not chunks:
        return False
    return chunks[0].get("source_file", "") in expected_sources


def run_reranker(reranker, reranker_name: str, questions, searcher):

    print(f"\n{'='*60}")
    print(f"  Running: {reranker_name}")
    print(f"{'='*60}")


    hits = []
    mrr_scores = []
    precision_at_5 = []

    for q in questions:
        # Retrieve candidates with full admin access
        candidates = searcher.vector_searcher.search(
            q.question, 
            top_k=TOP_K, 
            allowed_levels=["public", "operations", "admin"]
        )

        if not candidates:
            print(f"  [SKIP] No candidates for: {q.question[:60]}")
            continue

        reranked = reranker.rerank(q.question, candidates, top_k=RERANK_TOP_K)

        # Count how many reranked chunks match expected sources
        expected = set(q.expected_sources) if hasattr(q, "expected_sources") else set()
        
        found_ranks = []
        for rank, chunk in enumerate(reranked, start=1):
            source = chunk.get("metadata", {}).get("source") or chunk.get("source") or ""
            doc_id = chunk.get("metadata", {}).get("doc_id") or chunk.get("doc_id") or ""
            if any(exp in source or exp in doc_id for exp in expected):
                found_ranks.append(rank)

        # 1. Hit Rate (hit anywhere in the reranked results)
        hits.append(1 if len(found_ranks) > 0 else 0)

        # 2. MRR (1 / rank of first relevant match)
        rr = (1.0 / found_ranks[0]) if found_ranks else 0.0
        mrr_scores.append(rr)

        # 3. Precision@5 (relevant count / 5)
        p5 = len(found_ranks) / float(len(reranked) if reranked else 1)
        precision_at_5.append(p5)

        status = "OK" if found_ranks else "MISS"
        print(f"  [{status}] RR={rr:.2f} | {q.question[:55]}...")
        time.sleep(3)


    return {
        "name": reranker_name,
        "hit_rate": round(sum(hits) / len(hits) * 100, 2) if hits else 0.0,
        "mrr": round(sum(mrr_scores) / len(mrr_scores), 4) if mrr_scores else 0.0,
        "precision_at_5": round(sum(precision_at_5) / len(precision_at_5) * 100, 2) if precision_at_5 else 0.0,
    }



def main():
    print("\n" + "="*60)
    print("  RERANKER A/B COMPARISON")
    print("  CrossEncoder  vs  JEVReranker")
    print("="*60)

    try:
        questions = load_dataset("data/evaluation/evaluation_questions.json")
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


    print(f"\nLoaded {len(questions)} evaluation questions")
    print(f"Top-K retrieval: {TOP_K} | Rerank to: {RERANK_TOP_K} | Role: {ROLE}\n")

    print("Initializing HybridSearcher...")
    searcher = HybridSearcher(top_k=TOP_K, role=ROLE)

    print("Loading CrossEncoder reranker...")
    cross_encoder = Reranker()

    print("Loading JEVReranker...")
    jev = JEVReranker()

    cross_results = run_reranker(cross_encoder, "CrossEncoder (ms-marco-MiniLM-L-6-v2)", questions, searcher)
    jev_results   = run_reranker(jev,           "JEVReranker (TypeSafe AI)",               questions, searcher)

    print("\n\n" + "="*60)
    print("  COMPARISON RESULTS")
    print("="*60)
    print(f"  {'Metric':<25} {'CrossEncoder':>15} {'JEVReranker':>15}")
    print(f"  {'-'*25} {'-'*15} {'-'*15}")

    metrics = [
        ("MRR",             "mrr"),
        ("Top-1 Accuracy",  "top1_accuracy"),
        ("Avg Latency (s)", "avg_latency"),
    ]

    for label, key in metrics:
        ce_val  = cross_results[key]
        jev_val = jev_results[key]
        if key == "avg_latency":
            winner  = "[JEV]" if jev_val <= ce_val else "     "
            ce_mark = "[CE] " if jev_val >  ce_val else "     "
        else:
            winner  = "[JEV]" if jev_val >= ce_val else "     "
            ce_mark = "[CE] " if jev_val <  ce_val else "     "
        print(f"  {label:<25} {ce_mark} {ce_val:>13} {winner} {jev_val:>13}")

    print("\n" + "="*60)
    if jev_results["mrr"] > cross_results["mrr"]:
        print("  VERDICT: JEV wins on MRR!")
        print("  --> Set JEV_RERANKER_ENABLED=true in your .env to activate.")
    elif jev_results["mrr"] == cross_results["mrr"]:
        print("  VERDICT: Tied on MRR. Check latency cost before switching.")
    else:
        print("  VERDICT: CrossEncoder wins. Keep JEV_RERANKER_ENABLED=false.")
    print("="*60 + "\n")

    print("\n" + "=" * 60)
    print("           FINAL RERANKER COMPARISON (ROLE: ADMIN)")
    print("=" * 60)
    for res in [cross_results, jev_results]:
        print(f"\nModel: {res['name']}")
        print(f"  📌 Hit Rate:     {res['hit_rate']}%")
        print(f"  📌 MRR:          {res['mrr']}")
        print(f"  📌 Precision@5:  {res['precision_at_5']}%")
    print("=" * 60)


    searcher.close()


if __name__ == "__main__":
    main()
