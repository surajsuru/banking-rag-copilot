# banking-rag-copilot

> An enterprise-grade Retrieval-Augmented Generation (RAG) system built from scratch for banking operations.

## What This Project Is

An AI-powered knowledge copilot for a banking company. Employees ask natural language questions about:
- Payment processing (UPI, NEFT, RTGS, IMPS)
- API documentation and integration guides
- Error codes and troubleshooting (100+ standard codes)
- Transaction reversal procedures
- KYC / AML compliance policies
- Incident management runbooks & SEV escalation playbooks
- 3-Way reconciliation procedures
- Security controls and access policies

The system retrieves relevant context from a knowledge base using RAG and generates grounded answers with citations.

---

## Why This Project Exists

Most RAG tutorials hide complexity behind LangChain/LlamaIndex abstractions. This project builds every component manually so you understand exactly what happens internally:

- How documents are loaded, parsed across 9 formats, and cleaned
- How text is split into chunks (fixed sliding window vs. heading-aware structure chunking)
- How text becomes a dense embedding vector (384-dim sentence-transformers)
- How vector similarity search works (cosine similarity, dot product, L2 normalization)
- How vector databases (pgvector) store and index high-dimensional vectors
- How hybrid retrieval combines semantic + keyword search (BM25)
- How reranking improves result quality
- How access control (RBAC) is enforced at retrieval time
- How answers are grounded and cited with source tracking

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Document Parsing | PyMuPDF, python-docx, BeautifulSoup4, PyYAML, pandas |
| Data Normalization | unicodedata (NFKC), regex cleaning |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (384 dims, L2 normalized) |
| Vector Database | PostgreSQL + pgvector (Phase 6+) |
| LLM | Configurable (OpenAI / Groq / Local) (Phase 7+) |
| API | FastAPI (Phase 18+) |
| UI | Streamlit (Phase 19+) |

---

## Project Structure

`
banking-rag-copilot/
|
+-- data/
|   +-- raw/              # 40 synthetic banking documents (immutable source of truth)
|   +-- processed/        # Extracted, cleaned, chunked JSON artifacts
|   +-- evaluation/       # Evaluation datasets and benchmark results
|
+-- src/
|   +-- ingestion/        # Discovery, parser (9 formats), cleaner, chunker (fixed & heading-aware)
|   +-- embeddings/       # Embedding model, batching, normalization & similarity math
|   +-- database/         # PostgreSQL + pgvector schema and storage
|   +-- retrieval/        # Vector, keyword, hybrid search and reranking
|   +-- generation/       # Prompt construction and LLM interaction
|   +-- rag/              # Full pipeline orchestration
|   +-- security/         # Role-based access control
|   +-- evaluation/       # Retrieval and generation metrics
|
+-- app/
|   +-- api.py            # FastAPI endpoints
|   +-- ui.py             # Streamlit UI
|
+-- tests/
+-- config.py             # Central configuration (.env loader)
+-- requirements.txt      # Python dependencies
+-- docker-compose.yml
`

---

## Knowledge Base

40 synthetic banking documents across 9 formats:
- **PDF**: UPI Integration Guide, Error Code Reference, KYC Policy, IMPS Operations Guide, Payment Reconciliation
- **DOCX**: Account Management, Customer Onboarding, Incident Runbook, Release Notes, Reversal SOP
- **Markdown**: NEFT/RTGS Guide, API Handbook, KYC/AML Manual, Incident Playbook, Security Framework, Architecture Guide, Error Codes Manual, Release Notes v2/v3
- **TXT**: Support FAQ, Incident Logs
- **CSV**: Access Matrix, Document Catalog, Product Pricing Matrix
- **JSON / NDJSON**: Evaluation Questions, Event Schema, Support Tickets
- **YAML**: OpenAPI 3.0 Specification
- **HTML**: Change Management Policy, Data Retention Policy

> data/raw/ is the immutable source of truth. Never modify files inside it.

---

## Development Phases

| Phase | Status | Description |
|---|---|---|
| 1 - Foundation | ✅ Done | Project structure, venv, config, logging, git setup |
| 2 - Ingestion | ✅ Done | Loader, 9-format parsers, cleaner, chunker, pipeline runner (259 chunks) |
| 3 - Advanced Chunking | ✅ Done | Heading-aware structure chunking & strategy comparison |
| 4 - Embeddings Engine | ✅ Done | Embedder class with all-MiniLM-L6-v2, batching, L2 normalization, cosine similarity |
| 5 - Vector Storage | ✅ Done | PostgreSQL + pgvector setup, schema design, batch insertion (259 chunks) |
| 6 - Naive RAG | ✅ Done | First complete end-to-end question-answering pipeline (Groq + pgvector) |
| 7 - Citations & Grounding | ✅ Done | Citation extractor, token-overlap grounding score, unsupported sentence detection |
| 8 - Hybrid Retrieval | ✅ Done | BM25 + vector search with Reciprocal Rank Fusion (RRF), rank-bm25 |
| 9 - Reranking | ✅ Done | Cross-encoder reranking with cross-encoder/ms-marco-MiniLM-L-6-v2 |
| 10 - Access Control | ✅ Done | RBAC with 5 roles (public → admin), chunk-level access_level tagging, SQL filtering |
| 11 - Evaluation | ✅ Done | Retrieval benchmark: Hit Rate=1.0, MRR=0.88, Precision@5=0.29 (15 questions, role=admin) |
| 12 - API & UI | ✅ Done | FastAPI REST API (`/ask`, `/health`) + Streamlit chat UI with RBAC role selector |

---

## Quickstart

```bash
# 1. Clone repository
git clone https://github.com/surajsuru/banking-rag-copilot.git
cd banking-rag-copilot

# 2. Set up virtual environment
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env

# 5. Initialize PostgreSQL database & pgvector extension
python scripts/create_db.py
python scripts/test_connection.py

# 6. Run the Ingestion Pipeline
python -m src.ingestion.pipeline

# 7. Tag chunks with access levels
python -m scripts.tag_access_levels

# 8. Start the FastAPI backend (keep this terminal open)
uvicorn app.api:app --reload --port 8000

# 9. In a new terminal — start the Streamlit UI
streamlit run app/ui.py
```

> API docs available at: http://localhost:8000/docs
> Streamlit UI available at: http://localhost:8501

---

## Troubleshooting & Engineering Log

Encountered issues during setup or development? See our comprehensive [Troubleshooting & Problems Faced Log](TROUBLESHOOTING.md) detailing:
- Installing `pgvector` on Windows with PostgreSQL 18
- Fixing MSVC compilation errors (`vacuum_delay_point` API change in PostgreSQL 18)
- Database auto-creation and connection resolution
- Python path bootstrapping for standalone scripts

---

## Evaluation Benchmark Results (Phase 11)

Evaluated on 15 banking operations questions with `role=admin` (full document access), `top_k=5`.

| Metric | Score | Interpretation |
|---|---|---|
| **Hit Rate** | **1.00** | Correct document retrieved for all 15 questions |
| **MRR** | **0.88** | Correct document ranked #1 in 11/15 questions |
| **Precision@5** | **0.29** | ~1.5 relevant docs per 5 retrieved slots |

### Per-Question Results

| ID | Hit | MRR | P@5 | Answer Type | Note |
|---|---|---|---|---|---|
| Q001 | ✅ | 1.00 | 0.20 | direct | error_code_reference.pdf at rank 1 |
| Q002 | ✅ | 1.00 | 0.20 | multi_document | transaction_reversal_sop.docx at rank 1 |
| Q003 | ✅ | 0.50 | 0.20 | direct | api_openapi.yaml at rank 2 |
| Q004 | ✅ | 1.00 | 0.20 | direct | sla_policy.md at rank 1 |
| Q005 | ✅ | 0.20 | 0.20 | metadata | access_matrix.csv at rank 5 (CSV tabular format limits embedding quality) |
| Q006 | ✅ | 1.00 | 0.40 | multi_document | 2 of 3 expected sources retrieved |
| Q007 | ✅ | 1.00 | 0.20 | versioned | release_notes.docx at rank 1 |
| Q008 | ✅ | 1.00 | 0.20 | multi_document | imps_operations_guide.pdf at rank 1 |
| Q009 | ✅ | 1.00 | 0.20 | structured | transaction_event_schema.json at rank 1 |
| Q010 | ✅ | 1.00 | 1.00 | abstain | No expected sources — correctly handled |
| Q011 | ✅ | 1.00 | 0.40 | multi_document | Both customer_onboarding.docx + kyc_policy.pdf retrieved |
| Q012 | ✅ | 1.00 | 0.20 | direct | digital_payment_security.pdf at rank 1 |
| Q013 | ✅ | 1.00 | 0.20 | versioned | transaction_reversal_sop.docx at rank 1 |
| Q014 | ✅ | 0.50 | 0.20 | log_reasoning | error_code_reference.pdf at rank 2; sample_incident_logs.txt missed |
| Q015 | ✅ | 1.00 | 0.40 | public_reference | Both source_register.md + imps_operations_guide.pdf retrieved |

> Full results saved to [`data/evaluation/eval_results.json`](data/evaluation/eval_results.json)

---

## Chunking Strategy Benchmark (Phase 12)

To determine the optimal chunking configuration for our banking corpus, we benchmarked multiple chunk sizes, overlaps, and splitting algorithms against the golden evaluation dataset (15 test questions, `role=admin`, `top_k=5` via `HybridSearcher`).

### Strategy Comparison

| Strategy | Chunk Size (chars) | Overlap (chars) | Splitting Algorithm | Total Chunks | Hit Rate | MRR (Ranking Quality) | Precision@5 | Status |
|---|---|---|---|---|---|---|---|---|
| **`fixed_baseline`** | **500** | **100** | **Fixed sliding window** | **251** | **1.0000** | **0.8800** 🏆 | **0.2933** | **Selected Default** |
| `recursive` | 500 | 100 | Multi-level separator (`\n\n`, `\n`, `. `, ` `) | 249 | 1.0000 | 0.8722 | 0.3067 | Benchmark Candidate |
| `fixed_large` | 750 | 250 | Fixed sliding window | 205 | 1.0000 | 0.8556 | 0.3067 | Evaluated |
| `fixed_small` | 300 | 100 | Fixed sliding window | 485 | 1.0000 | 0.8167 | 0.2933 | Evaluated |

### Engineering Observations & Decision

1. **Why `fixed_baseline` (500 / 100) remains the chosen strategy:**
   - **Highest MRR (0.8800):** The golden source document is placed at rank #1 in the vast majority of retrieval queries, ensuring the top retrieved context fed to the LLM is directly relevant.
   - **Optimal Information Density:** With 251 chunks, it balances context completeness with granular semantic matching without diluting vector representations.
2. **Analysis of alternatives:**
   - **`fixed_small` (300 / 100):** Fragmented documents into 485 chunks, creating excessive noise that dropped MRR to **0.8167**.
   - **`fixed_large` (750 / 250):** Over-aggregated disparate banking policies into single chunks, reducing retrieval rank accuracy (MRR **0.8556**).
   - **`recursive` (500 / 100):** Achieved competitive performance (MRR **0.8722**, Precision@5 **0.3067**), validating that the ~500-character boundary size is mathematically the sweet spot for this corpus.

> Benchmark script available at [`scripts/benchmark_chunking.py`](scripts/benchmark_chunking.py) and raw evaluation data in [`data/evaluation/benchmark_results.json`](data/evaluation/benchmark_results.json).

---

## License

MIT License. For educational and portfolio use.
