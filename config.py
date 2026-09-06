"""
config.py
Central configuration for the Banking RAG Copilot project.
All settings are loaded from the .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root into os.environ
load_dotenv()

# ── Windows DLL Loading ─────────────────────────────────────────────
# In Python 3.8+ on Windows, DLLs required by C extensions (such as libpq.dll for psycopg2)
# are not loaded from PATH. They must be registered via os.add_dll_directory.
import sys
if sys.platform == "win32":
    pg_bin = os.getenv("PG_BIN_DIR", r"C:\Program Files\PostgreSQL\18\bin")
    if os.path.exists(pg_bin):
        try:
            os.add_dll_directory(pg_bin)
        except (AttributeError, OSError):
            pass


# ── Project Root ────────────────────────────────────────────────────
# Path(__file__).parent gives us the folder containing this file
# which is the project root (banking-rag-copilot/)
PROJECT_ROOT = Path(__file__).parent

# ── Data Directories ────────────────────────────────────────────────
# We read from .env, but fall back to sensible defaults if not set.
RAW_DATA_DIR      = PROJECT_ROOT / os.getenv("RAW_DATA_DIR", "data/raw")
PROCESSED_DATA_DIR = PROJECT_ROOT / os.getenv("PROCESSED_DATA_DIR", "data/processed")
EVALUATION_DATA_DIR = PROJECT_ROOT / os.getenv("EVALUATION_DATA_DIR", "data/evaluation")

# ── Logging ─────────────────────────────────────────────────────────
LOG_LEVEL  = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv(
    "LOG_FORMAT",
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# ── Database Configuration ─────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", "5432"))
DB_NAME     = os.getenv("DB_NAME", "banking_rag")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


