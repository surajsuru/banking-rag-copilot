import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.evaluation.dataset import load_dataset
from src.evaluation.metrics import hit_rate, mean_reciprocal_rank, precision_at_k
from src.rag.pipeline import NaiveRAGPipeline
from src.logger import get_logger
from config import RERANK_SCORE_THRESHOLD

logger = get_logger(__name__)

TOP_K            = 5
EVAL_OUTPUT_PATH = Path("data/evaluation/eval_results.json")
AVG_CHARS_PER_CHUNK = 600   # avg chunk size in chars
CHARS_PER_TOKEN     = 4     # ~4 chars per token


# ── Guard Efficiency helpers ──────────────────────────────────────────────────

def compute_guard_metrics(retrieved_chunks: list, expected_sources: list, is_negative: bool):
    """
    Splits retrieved chunks into accepted/rejected based on rerank_score threshold.
    Returns post-guard context precision, noise stats, and token savings.
    """
    expected = set(expected_sources)

    def source_match(chunk):
        src = chunk.get("source_file") or chunk.get("source") or ""
        return any(exp in src for exp in expected)

    accepted = [c for c in retrieved_chunks if c.get("rerank_score", 0.0) >= RERANK_SCORE_THRESHOLD]
    rejected = [c for c in retrieved_chunks if c.get("rerank_score", 0.0) <  RERANK_SCORE_THRESHOLD]

    n_acc = len(accepted)
    n_rej = len(rejected)

    rel_acc  = sum(1 for c in accepted if source_match(c))
    irr_acc  = n_acc - rel_acc

    if n_acc > 0:
        ctx_prec = rel_acc / n_acc
    else:
        ctx_prec = 1.0 if is_negative else 0.0  # if nothing accepted: perfect for negatives, bad for positives

    tokens_saved = int(n_rej * AVG_CHARS_PER_CHUNK / CHARS_PER_TOKEN)

    return {
        "ctx_precision":  round(ctx_prec * 100, 1),
        "n_accepted":     n_acc,
        "n_rejected":     n_rej,
        "tokens_saved":   tokens_saved,
        "guard_correct":  1 if (is_negative and n_acc == 0) else 0,
    }


# ── Main evaluation ───────────────────────────────────────────────────────────

def run_evaluation():
    # 1. Load questions
    questions = load_dataset("data/evaluation/evaluation_questions.json")

    # 2. Initialize pipeline (admin role = full access to all chunks)
    pipeline = NaiveRAGPipeline(top_k=TOP_K, role="admin")

    results = []
    total_hit, total_mrr, total_p5 = 0.0, 0.0, 0.0

    # Guard efficiency accumulators
    total_ctx_prec   = 0.0
    total_noise_rej  = 0
    total_tokens_saved = 0
    guard_total      = 0
    guard_correct    = 0

    print("\n" + "=" * 90)
    print(f"  BANKING RAG COPILOT — RETRIEVAL EVALUATION")
    print(f"  CrossEncoder (ms-marco-MiniLM-L-6-v2) | Threshold: {RERANK_SCORE_THRESHOLD}")
    print("=" * 90)
    print(f"{'ID':<6} {'Cat':<14} {'Hit':>5} {'MRR':>6} {'P@5':>6} {'CtxPrc':>8} {'Acc/Rej':>8}  Question")
    print("-" * 90)

        # 3. Run each question directly through searcher (raw Pre-Guard retrieval)
    for q in questions:
        is_negative = getattr(q, "answer_type", "") == "abstain"
        category    = getattr(q, "category",    "unknown")

        start = time.time()
        # Call searcher directly to get all 5 candidates with rerank_score BEFORE filtering
        raw_chunks = pipeline.searcher.search(q.question)
        elapsed = time.time() - start

        raw_sources = [c.get("source_file", "") for c in raw_chunks]

        # 4. Pre-Guard metrics (classic retrieval on all raw retrieved chunks)
        hr  = hit_rate(raw_sources, q.expected_sources)
        mrr = mean_reciprocal_rank(raw_sources, q.expected_sources)
        p5  = precision_at_k(raw_sources, q.expected_sources, k=TOP_K)

        total_hit += hr
        total_mrr += mrr
        total_p5  += p5

        # 5. Post-Guard metrics (splits raw_chunks into accepted >= 0.3 and rejected < 0.3)
        gm = compute_guard_metrics(raw_chunks, q.expected_sources, is_negative)
        total_ctx_prec   += gm["ctx_precision"]
        total_noise_rej  += gm["n_rejected"]
        total_tokens_saved += gm["tokens_saved"]
        if is_negative:
            guard_total   += 1
            guard_correct += gm["guard_correct"]

        acc_rej_tag = f"{gm['n_accepted']}acc/{gm['n_rejected']}rej"
        print(f"{q.id:<6} {category:<14} {hr:>5.2f} {mrr:>6.3f} {p5:>6.3f} {gm['ctx_precision']:>7.1f}% {acc_rej_tag:>8}  {q.question[:45]}")

        results.append({
            "id":               q.id,
            "category":         category,
            "question":         q.question,
            "answer_type":      getattr(q, "answer_type", ""),
            "expected_sources": q.expected_sources,
            "retrieved_sources": raw_sources,
            "hit_rate":         hr,
            "mrr":              mrr,
            "precision_at_5":   p5,
            "ctx_precision":    gm["ctx_precision"],
            "n_accepted":       gm["n_accepted"],
            "n_rejected":       gm["n_rejected"],
            "tokens_saved":     gm["tokens_saved"],
            "latency_sec":      round(elapsed, 3),
        })

    n = len(questions)

    # ── Summary tables ────────────────────────────────────────────────────────
    print("=" * 90)
    print(f"{'AVG':<6} {'':<14} {total_hit/n:>5.2f} {total_mrr/n:>6.3f} {total_p5/n:>6.3f} {total_ctx_prec/n:>7.1f}%")
    print("=" * 90)

    # Pre-Guard summary
    print("\n" + "=" * 62)
    print("  RETRIEVAL METRICS  (Pre-Guard — all retrieved chunks)")
    print("=" * 62)
    print(f"  {'Hit Rate':38} {round(total_hit/n*100,1):>5}%")
    print(f"  {'MRR (Mean Reciprocal Rank)':38} {round(total_mrr/n,4):>6}")
    print(f"  {'Raw Precision@'+str(TOP_K)+' (classic)':38} {round(total_p5/n*100,1):>5}%")
    print(f"\n  NOTE: Raw Precision@{TOP_K} capped at {100//TOP_K}% for single-chunk questions.")

    # Post-Guard efficiency report
    noise_pct = round(total_noise_rej / (n * TOP_K) * 100, 1)
    print("\n" + "=" * 62)
    print("  RAG RETRIEVAL & GUARD EFFICIENCY REPORT")
    print("=" * 62)
    print(f"  📌 {'Raw Precision@'+str(TOP_K)+' (Pre-Filter)':36} {round(total_p5/n*100,1):>5}%  (All {TOP_K} retrieved)")
    print(f"  📌 {'Context Precision (Post-Guard)':36} {round(total_ctx_prec/n,1):>5}%  (Only accepted chunks)")
    print(f"  📌 {'Noise Reduction':36} {noise_pct:>5}%  ({round(total_noise_rej/n,1)} irrelevant chunks blocked/query)")
    print(f"  📌 {'Prompt Token Savings (total run)':36} ~{total_tokens_saved:,} tokens saved")
    print(f"  📌 {'Guard Accuracy (Category D)':36} {round(guard_correct/guard_total*100,1) if guard_total else 0:>5}%  (OOD/adversarial correctly declined)")

    print("\n" + "=" * 62)
    print("  SUMMARY")
    print("=" * 62)
    print(f"  Total questions     : {n}")
    print(f"  Hit Rate            : {round(total_hit/n*100,1)}%")
    print(f"  MRR                 : {round(total_mrr/n,4)}")
    print(f"  Context Precision   : {round(total_ctx_prec/n,1)}%   ← key production metric")
    print(f"  Guard Accuracy      : {round(guard_correct/guard_total*100,1) if guard_total else 0}%   ← blocks OOD / adversarial")
    print("=" * 62 + "\n")

    # 6. Save full results to JSON
    EVAL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EVAL_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "results": results,
            "summary": {
                "total_questions":    n,
                "avg_hit_rate":       round(total_hit / n, 4),
                "avg_mrr":            round(total_mrr / n, 4),
                "avg_precision_5":    round(total_p5 / n, 4),
                "avg_ctx_precision":  round(total_ctx_prec / n, 1),
                "noise_reduction_pct": noise_pct,
                "total_tokens_saved": total_tokens_saved,
                "guard_accuracy":     round(guard_correct / guard_total * 100, 1) if guard_total else 0,
            }
        }, f, indent=2)

    logger.info(f"Results saved to {EVAL_OUTPUT_PATH}")
    pipeline.close()


if __name__ == "__main__":
    run_evaluation()
