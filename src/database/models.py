"""
models.py

Creates the database table for storing document chunks and their vector embeddings.
Run this once to set up the schema before inserting any data.
"""

import psycopg2
from src.logger import get_logger

logger = get_logger(__name__)


CREATE_TABLE_SQL = """
-- Enable vector extension (safe to run multiple times)
CREATE EXTENSION IF NOT EXISTS vector;

-- Main chunks table
CREATE TABLE IF NOT EXISTS chunks (
    -- Unique identifier for each chunk
    chunk_id      TEXT PRIMARY KEY,

    -- The actual text content of the chunk
    text          TEXT NOT NULL,

    -- Which file this chunk came from
    source_file   TEXT NOT NULL,
    source_path   TEXT,
    extension     TEXT,

    -- Position within the parent document
    chunk_index   INTEGER,
    total_chunks  INTEGER,

    -- Which chunking strategy was used
    strategy      TEXT DEFAULT 'fixed',

    -- The 384-dimensional embedding vector
    -- This is what makes semantic search possible
    embedding     vector(384),

    -- When this chunk was inserted
    created_at    TIMESTAMP DEFAULT NOW()
);

-- Create an index for fast vector similarity search
-- HNSW = Hierarchical Navigable Small World graph
-- cosine = we're using cosine similarity as our distance metric
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
    ON chunks
    USING hnsw (embedding vector_cosine_ops);
"""


def create_tables(connection) -> None:
    """
    Creates the chunks table and vector index in PostgreSQL.
    Safe to call multiple times (uses IF NOT EXISTS).
    """
    with connection.cursor() as cursor:
        cursor.execute(CREATE_TABLE_SQL)
        connection.commit()
    logger.info("Database tables created successfully.")
