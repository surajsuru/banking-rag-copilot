"""
ingest_to_db.py

Step 1 of Phase 5:
1. Loads all 259 chunks from data/processed/chunks.json
2. Generates 384-dimensional dense vectors using Embedder (sentence-transformers/all-MiniLM-L6-v2)
3. Connects to PostgreSQL and stores chunks + embeddings into the 'chunks' table in batches.

Usage:
    python scripts/ingest_to_db.py
"""

import sys
import json
import time
from pathlib import Path

# Add project root to sys.path so we can import from src and config
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.logger import get_logger
from src.embeddings.embedder import Embedder
from src.database.vector_store import connect, save_chunks

logger = get_logger(__name__)


def main():
    chunks_path = PROJECT_ROOT / "data" / "processed" / "chunks.json"

    print("=" * 60)
    print("PHASE 5: INGESTING CHUNKS INTO POSTGRESQL + PGVECTOR")
    print("=" * 60)

    # 1. Load chunks from JSON
    print(f"\n[Step 1/3] Loading chunks from: {chunks_path.name}")
    if not chunks_path.exists():
        print(f"Error: {chunks_path} not found. Please run ingestion first.")
        return

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"--> Loaded {len(chunks)} chunks from disk.")

    # 2. Generate embeddings
    print(f"\n[Step 2/3] Generating dense embeddings using sentence-transformers...")
    print("--> Model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)")
    embedder = Embedder(batch_size=32)

    start_time = time.time()
    embedded_chunks = embedder.embed_chunks(chunks, show_progress=True)
    embed_duration = time.time() - start_time

    print(f"--> Embedded {len(embedded_chunks)} chunks in {embed_duration:.2f}s!")
    print(f"--> Sample embedding length: {len(embedded_chunks[0]['embedding'])} floats")

    # 3. Save into PostgreSQL
    print(f"\n[Step 3/3] Inserting embedded chunks into PostgreSQL...")
    conn = connect()

    save_start = time.time()
    inserted_count = save_chunks(conn, embedded_chunks, batch_size=50)
    save_duration = time.time() - save_start

    # Verify table row count
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM chunks;")
        total_in_db = cur.fetchone()[0]

    conn.close()

    print(f"--> Inserted {inserted_count} chunks in {save_duration:.2f}s.")
    print(f"--> Total rows now in 'chunks' table: {total_in_db}")
    print("\n" + "=" * 60)
    print("INGESTION COMPLETE! Vector database is now populated.")
    print("=" * 60)


if __name__ == "__main__":
    main()
