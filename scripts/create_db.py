"""
create_db.py

Run this ONCE to create the banking_rag PostgreSQL database.
Usage: python scripts/create_db.py
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT} as user '{DB_USER}'...")

# Step 1: Connect to the default 'postgres' database
# (We cannot connect to 'banking_rag' if it doesn't exist yet)
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname="postgres",   # Always exists in every PostgreSQL installation
    user=DB_USER,
    password=DB_PASSWORD
)

# Required to run CREATE DATABASE outside a transaction block
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cursor = conn.cursor()

# Step 2: Check if the target database already exists
cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
already_exists = cursor.fetchone()

if already_exists:
    print(f"INFO: Database '{DB_NAME}' already exists. Nothing to do.")
else:
    cursor.execute(f"CREATE DATABASE {DB_NAME}")
    print(f"SUCCESS: Database '{DB_NAME}' created!")

cursor.close()
conn.close()
print("Done.")
