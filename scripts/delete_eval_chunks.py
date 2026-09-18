"""
Deletes all chunks for evaluation_questions.json from the database.
This file should NOT be in the vector store — it is used only for evaluation,
not as a knowledge base document.
"""
from src.database.vector_store import connect

conn = connect()
cur = conn.cursor()

cur.execute("DELETE FROM chunks WHERE source_file = 'evaluation_questions.json';")
deleted = cur.rowcount

conn.commit()
cur.close()
conn.close()

print(f"Done. Deleted {deleted} chunks for 'evaluation_questions.json'.")
