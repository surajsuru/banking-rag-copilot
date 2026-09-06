"""
test_search.py

Performs a semantic similarity search directly against PostgreSQL + pgvector.

Usage:
    python scripts/test_search.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.embeddings.embedder import Embedder
from src.database.vector_store import connect, search


def run_query(conn, embedder, query_text: str, top_k: int = 3):
    print("\n" + "-" * 60)
    print(f"QUERY: \"{query_text}\"")
    print("-" * 60)

    # 1. Convert user text query into a 384-dimensional vector
    query_vector = embedder.embed_text(query_text)

    # 2. Run similarity search in PostgreSQL
    results = search(conn, query_vector, top_k=top_k)

    # 3. Print retrieved results
    for i, res in enumerate(results, 1):
        print(f"\n[Rank {i}] Score: {res['similarity']:.4f} | Source: {res['source_file']}")
        print(f"Text snippet: {res['text'][:180].strip()}...")


def main():
    conn = connect()
    embedder = Embedder()

    print("=" * 60)
    print("TESTING SEMANTIC SEARCH (POSTGRESQL + PGVECTOR)")
    print("=" * 60)

    # Test Query 1: Banking operations & reversal
    run_query(
        conn,
        embedder,
        query_text="How to reverse a failed IMPS transaction and what is the turnaround time?",
        top_k=2
    )

    # Test Query 2: API limits
    run_query(
        conn,
        embedder,
        query_text="What is the daily transaction limit for UPI payments?",
        top_k=2
    )

    conn.close()
    print("\n" + "=" * 60)
    print("SEMANTIC SEARCH VERIFIED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
