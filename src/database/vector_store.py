"""
vector_store.py

Simple interface for storing and searching chunks in PostgreSQL + pgvector.

4 operations only:
1. connect()       - connect to the database
2. save_chunks()   - insert chunks with their embeddings
3. search()        - find similar chunks using vector similarity
4. delete_all()    - clear the table (useful during development)
"""

import json
import psycopg2
from typing import List, Dict, Any

from src.logger import get_logger
from src.database.models import create_tables
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

logger = get_logger(__name__)


def connect() -> psycopg2.extensions.connection:
    """
    Opens a connection to the PostgreSQL database.
    Call this once at the start of your script.
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    logger.info(f"Connected to database '{DB_NAME}' on {DB_HOST}:{DB_PORT}")

    # Ensure table and index exist
    create_tables(conn)

    return conn


def save_chunks(conn, chunks: List[Dict[str, Any]], batch_size: int = 100) -> int:
    """
    Inserts a list of embedded chunks into the database.

    Each chunk must already have an 'embedding' key (list of 384 floats).
    Inserts in batches of 100 for efficiency.
    Uses ON CONFLICT DO NOTHING to safely skip duplicate chunk_ids.

    Returns: number of chunks successfully inserted.
    """
    if not chunks:
        logger.warning("No chunks to save.")
        return 0

    INSERT_SQL = """
        INSERT INTO chunks (
            chunk_id, text, source_file, source_path,
            extension, chunk_index, total_chunks,
            strategy, embedding
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
        ON CONFLICT (chunk_id) DO NOTHING;
    """

    inserted = 0

    # Process in batches
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]

        with conn.cursor() as cursor:
            for chunk in batch:
                # Convert the embedding list to a string PostgreSQL understands
                embedding_str = "[" + ",".join(str(v) for v in chunk["embedding"]) + "]"

                cursor.execute(INSERT_SQL, (
                    chunk.get("chunk_id", ""),
                    chunk.get("text", ""),
                    chunk.get("source_file", ""),
                    chunk.get("source_path", ""),
                    chunk.get("extension", ""),
                    chunk.get("chunk_index", 0),
                    chunk.get("total_chunks", 0),
                    chunk.get("strategy", "fixed"),
                    embedding_str,
                ))
                inserted += 1

        conn.commit()
        logger.info(f"Saved batch {i // batch_size + 1}: {len(batch)} chunks.")

    logger.info(f"Total chunks saved to database: {inserted}")
    return inserted


def search(
    conn,
    query_embedding: List[float],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Finds the top_k most semantically similar chunks to a query vector.

    Uses cosine distance (<=>) — lower distance = higher similarity.

    Returns a list of result dicts with text, source_file, and similarity score.
    """
    SEARCH_SQL = """
        SELECT
            chunk_id,
            text,
            source_file,
            chunk_index,
            1 - (embedding <=> %s::vector) AS similarity
        FROM chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """

    # Convert list to PostgreSQL vector string format
    embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

    with conn.cursor() as cursor:
        cursor.execute(SEARCH_SQL, (embedding_str, embedding_str, top_k))
        rows = cursor.fetchall()

    results = []
    for row in rows:
        results.append({
            "chunk_id":    row[0],
            "text":        row[1],
            "source_file": row[2],
            "chunk_index": row[3],
            "similarity":  round(float(row[4]), 4),
        })

    return results


def delete_all(conn) -> None:
    """
    Deletes all rows from the chunks table.
    Useful during development when re-ingesting with updated embeddings.
    """
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM chunks;")
        conn.commit()
    logger.info("All chunks deleted from database.")
