"""
migrate_access_level.py

Phase 10 - RBAC Migration Script.

Adds the 'access_level' column to the existing chunks table.
Safe to run multiple times (uses IF NOT EXISTS).
"""

from src.database.vector_store import connect
from src.logger import get_logger

logger = get_logger(__name__)


def run_migration():
    conn = connect()
    cur = conn.cursor()

    # Add access_level column — defaults all existing chunks to 'public'
    cur.execute("""
        ALTER TABLE chunks
        ADD COLUMN IF NOT EXISTS access_level TEXT DEFAULT 'public';
    """)
    conn.commit()

    # Verify the column exists
    cur.execute("""
        SELECT column_name, data_type, column_default
        FROM information_schema.columns
        WHERE table_name = 'chunks' AND column_name = 'access_level';
    """)
    row = cur.fetchone()
    if row:
        print(f"Column '{row[0]}' | type: {row[1]} | default: {row[2]}")
        print("Migration done: access_level column added successfully.")
    else:
        print("ERROR: Column was not created.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    run_migration()
