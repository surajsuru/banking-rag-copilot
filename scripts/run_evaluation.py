import json
import time
from pathlib import Path

from src.evaluation.dataset import load_dataset
from src.evaluation.metrics import hit_rate, mean_reciprocal_rank, precision_at_k
from src.rag.pipeline import NaiveRAGPipeline
from src.logger import get_logger

logger = get_logger(__name__)

TOP_K = 5
EVAL_OUTPUT_PATH = Path("data/evaluation/eval_results.json")


def run_evaluation():
    # 1. Load questions
    questions = load_dataset()

    # 2. Initialize pipeline
    pipeline = NaiveRAGPipeline(top_k=TOP_K, role="admin")

    results = []
    total_hit, total_mrr, total_p5 = 0.0, 0.0, 0.0

    print("\n" + "=" * 80)
    print(f"{'ID':<6} {'HitRate':>8} {'MRR':>8} {'P@5':>8}  Question")
    print("=" * 80)

    # 3. Run each question through the pipeline
    for q in questions:
        start = time.time()
        result = pipeline.ask(q.question)
        elapsed = time.time() - start

        retrieved_sources = result["sources"]

        # 4. Compute metrics
        hr  = hit_rate(retrieved_sources, q.expected_sources)
        mrr = mean_reciprocal_rank(retrieved_sources, q.expected_sources)
        p5  = precision_at_k(retrieved_sources, q.expected_sources, k=TOP_K)

        total_hit += hr
        total_mrr += mrr
        total_p5  += p5

        print(f"{q.id:<6} {hr:>8.2f} {mrr:>8.3f} {p5:>8.3f}  {q.question[:55]}")

        results.append({
            "id":               q.id,
            "question":         q.question,
            "answer_type":      q.answer_type,
            "expected_sources": q.expected_sources,
            "retrieved_sources": retrieved_sources,
            "hit_rate":         hr,
            "mrr":              mrr,
            "precision_at_5":   p5,
            "latency_sec":      round(elapsed, 3),
        })

    n = len(questions)
    print("=" * 80)
    print(f"{'AVG':<6} {total_hit/n:>8.2f} {total_mrr/n:>8.3f} {total_p5/n:>8.3f}")
    print("=" * 80)

    # 5. Save results to file
    EVAL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EVAL_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"results": results, "summary": {
            "total_questions": n,
            "avg_hit_rate":    round(total_hit / n, 4),
            "avg_mrr":         round(total_mrr / n, 4),
            "avg_precision_5": round(total_p5 / n, 4),
        }}, f, indent=2)

    logger.info(f"Results saved to {EVAL_OUTPUT_PATH}")
    pipeline.close()

if __name__ == "__main__":
    run_evaluation()

