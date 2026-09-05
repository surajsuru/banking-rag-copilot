"""
test_connection.py

Verifies that the database connection works and tables are created.
Usage: python -m scripts.test_connection
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database.vector_store import connect

conn = connect()
print("Connection successful!")

# Verify the chunks table exists
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM chunks;")
count = cursor.fetchone()[0]
print(f"Chunks table exists. Current row count: {count}")

cursor.close()
conn.close()
print("All good - ready for next step!")
