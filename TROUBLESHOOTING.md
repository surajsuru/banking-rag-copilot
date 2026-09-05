# Problems Faced & Engineering Solutions Log

This document tracks all real-world technical hurdles, compatibility issues, alternatives considered, and step-by-step solutions encountered during the development of **banking-rag-copilot**.

---

## Table of Contents
1. [Issue 1: PostgreSQL Server-Side Extension `pgvector` Missing on Windows](#issue-1-postgresql-server-side-extension-pgvector-missing-on-windows)
2. [Issue 2: pgvector Compilation Error on PostgreSQL 18 (`vacuum_delay_point`)](#issue-2-pgvector-compilation-error-on-postgresql-18-vacuum_delay_point)
3. [Issue 3: Database `banking_rag` Does Not Exist](#issue-3-database-banking_rag-does-not-exist)
4. [Issue 4: Standalone Python Scripts Failing with `ModuleNotFoundError: No module named 'src'`](#issue-4-standalone-python-scripts-failing-with-modulenotfounderror-no-module-named-src)

---

## Issue 1: PostgreSQL Server-Side Extension `pgvector` Missing on Windows

### 1. Problem Description
When executing `CREATE EXTENSION IF NOT EXISTS vector;` from Python or `psql`, PostgreSQL returned:
```text
ERROR: extension "vector" is not available
HINT: The extension must first be installed on the system where PostgreSQL is running.
```
Although `pip install pgvector` was installed in the Python virtual environment, this only installs the **Python client adapter**. The actual PostgreSQL server requires C-extension files (`vector.dll`, `vector.control`, and `vector--*.sql`) in the PostgreSQL installation directory (`C:\Program Files\PostgreSQL\18`).

### 2. Alternatives Explored

| Option | Assessment | Outcome |
|---|---|---|
| **A. Pre-built binary ZIP** | Checked pgvector GitHub Releases for pre-compiled Windows `.dll` binaries for PostgreSQL 18. | Official pgvector releases do not distribute pre-compiled Windows binaries for PG 18; only source code archives are provided. |
| **B. Conda-forge package** | Tested installing via `conda install -c conda-forge pgvector`. | Installs into the Conda environment's isolated PostgreSQL instance, not into the existing Windows PostgreSQL 18 service running on port 5432. |
| **C. In-Memory / SQLite fallback** | Considered storing embeddings in JSON/SQLite and computing cosine similarity via pure NumPy. | Good fallback for small datasets, but defeats the goal of learning production-grade vector databases, SQL integration, and HNSW indexing. |
| **D. Compile from Source using MSVC (`nmake`)** | Compile `pgvector` directly against the installed PostgreSQL 18 C-headers using Microsoft Visual Studio C++ Build Tools. | **Selected Solution** — Native, highest performance, and directly attaches to the system PostgreSQL 18 service. |

### 3. Solution
1. Installed **Visual Studio Build Tools 2026 / 2022** with the **"Desktop development with C++"** workload.
2. Opened **`x64 Native Tools Command Prompt for VS`** as **Administrator**.
3. Set the PostgreSQL root directory:
   ```cmd
   set "PGROOT=C:\Program Files\PostgreSQL\18"
   ```

---

## Issue 2: pgvector Compilation Error on PostgreSQL 18 (`vacuum_delay_point`)

### 1. Problem Description
When compiling the `v0.8.0` tag using `nmake /F Makefile.win`, compilation failed with:
```text
src\hnswvacuum.c(52): error C2198: 'void vacuum_delay_point(bool)': too few arguments for call
src\hnswvacuum.c(348): error C2198: 'void vacuum_delay_point(bool)': too few arguments for call
src\hnswvacuum.c(460): error C2198: 'void vacuum_delay_point(bool)': too few arguments for call
NMAKE : fatal error U1077: 'cl ... src\hnswvacuum.c /Fosrc\hnswvacuum.obj' : return code '0x2'
Stop.
```

### 2. Root Cause Analysis
- **PostgreSQL 18** changed the internal signature of the `vacuum_delay_point()` function in the PostgreSQL core C API:
  - **PG <= 17:** `void vacuum_delay_point(void);` (0 arguments)
  - **PG 18:** `void vacuum_delay_point(bool is_analyze);` (1 required boolean argument)
- The tagged release `v0.8.0` of `pgvector` was authored prior to the PostgreSQL 18 API signature change and did not pass `is_analyze`.

### 3. Solution
The upstream `pgvector` **`master`** branch (and releases `v0.8.6`+) already resolved this breaking API change.

In the **x64 Native Tools Command Prompt (as Administrator)**:
```cmd
cd %TEMP%\pgvector
git checkout master
git pull
nmake /F Makefile.win
nmake /F Makefile.win install
```

**Verification in PostgreSQL:**
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d banking_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d banking_rag -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```
**Result:**
```text
CREATE EXTENSION
 extname | extversion
---------+------------
 vector  | 0.8.6
(1 row)
```

---

## Issue 3: Database `banking_rag` Does Not Exist

### 1. Problem Description
When initially connecting with Python:
```text
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed:
FATAL: database "banking_rag" does not exist
```

### 2. Root Cause Analysis
PostgreSQL server was active, but the application-specific database `banking_rag` had not yet been created.

### 3. Solution
Created a dedicated idempotent creation script ([`scripts/create_db.py`](file:///c:/AI%20ML%20Engineer%20path/banking-rag-copilot/scripts/create_db.py)) that connects to the default `postgres` maintenance database with `ISOLATION_LEVEL_AUTOCOMMIT` to create `banking_rag`:
```python
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    dbname="postgres",
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
if not cur.fetchone():
    cur.execute(f"CREATE DATABASE {DB_NAME}")
cur.close()
conn.close()
```

---

## Issue 4: Standalone Python Scripts Failing with `ModuleNotFoundError: No module named 'src'`

### 1. Problem Description
Running standalone test scripts directly via:
```powershell
python scripts/test_connection.py
```
raised:
```text
ModuleNotFoundError: No module named 'src'
```

### 2. Root Cause Analysis
When executing a script directly (`python scripts/test_connection.py`), Python puts `scripts/` at `sys.path[0]` rather than the project root directory.

### 3. Solution
Two solutions implemented:
1. **Run as a module:**
   ```powershell
   python -m scripts.test_connection
   ```
2. **Path bootstrapping in script header:**
   Added standard path resolution in [`scripts/test_connection.py`](file:///c:/AI%20ML%20Engineer%20path/banking-rag-copilot/scripts/test_connection.py):
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
   ```
   Now both execution methods work seamlessly.
