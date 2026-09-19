"""
benchmark_chunking.py

Runs the full ingestion + evaluation pipeline for multiple chunking strategies
and prints a comparison table of retrieval metrics.

Strategies tested:
  - fixed_small:   chunk_size=300, overlap=100, strategy='fixed'
  - fixed_baseline: chunk_size=500, overlap=100, strategy='fixed'  ← current
  - fixed_large:   chunk_size=750, overlap=250, strategy='fixed'
  - recursive:     chunk_size=500, overlap=100, strategy='recursive'
"""
import json
from pathlib import Path
from src.database.vector_store import connect
from src.ingestion.pipeline import run_ingestion_pipeline
from src.database.models import create_tables
from src.database.vector_store import save_chunks
from src.embeddings.embedder import Embedder
from src.evaluation.dataset import load_dataset
from src.evaluation.metrics import hit_rate, mean_reciprocal_rank, precision_at_k
from src.retrieval.hybrid_search import HybridSearcher
from src.logger import get_logger

logger = get_logger(__name__)

STRATEGIES = [
    {"name": "fixed_small",    "chunk_size": 300, "overlap": 100, "strategy": "fixed"},
    {"name": "fixed_baseline", "chunk_size": 500, "overlap": 100, "strategy": "fixed"},
    {"name": "fixed_large",    "chunk_size": 750, "overlap": 250, "strategy": "fixed"},
    {"name": "recursive",      "chunk_size": 500, "overlap": 100, "strategy": "recursive"},
]

TOP_K = 5
RESULTS_PATH = Path("data/evaluation/benchmark_results.json")


def clear_chunks(conn):
    """Deletes all rows from the chunks table to start fresh."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM chunks;")
        deleted = cur.rowcount
    conn.commit()
    logger.info(f"Cleared {deleted} chunks from database.")



def ingest_and_embed(conn, chunk_size: int, overlap: int, strategy: str):
    """
    Runs ingestion with given chunk settings,
    embeds all chunks and inserts into DB.
    """
    # 1. Re-ingest raw documents with new chunking settings
    chunks = run_ingestion_pipeline(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        strategy=strategy,
    )

    # 2. Embed all chunks
    embedder = Embedder()
    texts = [c["text"] for c in chunks]
    embeddings = embedder.embed_batch(texts)

    # 3. Attach embedding to each chunk
    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb
        chunk["access_level"] = "public"  # default — will be overridden by tag script

    # 4. Insert into database
    create_tables(conn)
    save_chunks(conn, chunks)

    logger.info(f"Inserted {len(chunks)} chunks (strategy={strategy}, size={chunk_size}, overlap={overlap})")
    return len(chunks)


from scripts.tag_access_levels import classify_access_level

def tag_access_levels(conn):
    """Re-tags all chunks with correct access levels after re-ingestion."""
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT source_file FROM chunks;")
        source_files = [row[0] for row in cur.fetchall()]

    with conn.cursor() as cur:
        for source_file in source_files:
            level = classify_access_level(source_file)
            cur.execute(
                "UPDATE chunks SET access_level = %s WHERE source_file = %s;",
                (level, source_file)
            )
    conn.commit()
    logger.info(f"Tagged {len(source_files)} source files with access levels.")


def evaluate() -> dict:
    """Runs the 15-question evaluation and returns aggregate scores."""
    questions = load_dataset()
    searcher = HybridSearcher(top_k=TOP_K, role="admin")

    total_hit, total_mrr, total_p5 = 0.0, 0.0, 0.0

    for q in questions:
        results = searcher.search(q.question)
        retrieved_sources = list(dict.fromkeys(r["source_file"] for r in results))

        total_hit += hit_rate(retrieved_sources, q.expected_sources)
        total_mrr += mean_reciprocal_rank(retrieved_sources, q.expected_sources)
        total_p5  += precision_at_k(retrieved_sources, q.expected_sources, k=TOP_K)

    searcher.close()
    n = len(questions)
    return {
        "hit_rate":    round(total_hit / n, 4),
        "mrr":         round(total_mrr / n, 4),
        "precision_5": round(total_p5  / n, 4),
    }


def main():
    all_results = []

    print("\n" + "=" * 75)
    print(f"{'Strategy':<20} {'Chunks':>7} {'HitRate':>9} {'MRR':>9} {'P@5':>9}")
    print("=" * 75)

    for cfg in STRATEGIES:
        logger.info(f"\n{'='*60}")
        logger.info(f"Running strategy: {cfg['name']}")

        conn = connect()

        # Step 1: Clear DB
        clear_chunks(conn)

        # Step 2: Ingest + Embed
        n_chunks = ingest_and_embed(conn, cfg["chunk_size"], cfg["overlap"], cfg["strategy"])

        # Step 3: Tag access levels
        tag_access_levels(conn)

        conn.close()

        # Step 4: Evaluate
        scores = evaluate()

        result = {**cfg, "n_chunks": n_chunks, **scores}
        all_results.append(result)

        print(
            f"{cfg['name']:<20} {n_chunks:>7} "
            f"{scores['hit_rate']:>9.4f} {scores['mrr']:>9.4f} {scores['precision_5']:>9.4f}"
        )

    print("=" * 75)

    # Save results
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(all_results, f, indent=2)

    logger.info(f"Benchmark results saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
