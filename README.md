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
| 4 - Embeddings Engine | ✅ Done | Embedder class with ll-MiniLM-L6-v2, batching, L2 normalization, cosine similarity |
| 5 - Vector Storage | ⏳ Next | PostgreSQL + pgvector setup, schema design, batch insertion |
| 6 - Naive RAG | ⏳ Pending | First complete end-to-end question-answering pipeline |
| 7 - Citations & Grounding | ⏳ Pending | Source tracking & hallucination prevention |
| 8 - Hybrid Retrieval | ⏳ Pending | BM25 keyword search + vector search |
| 9 - Reranking | ⏳ Pending | Cross-encoder candidate reranking |
| 10 - Access Control | ⏳ Pending | Role-based document filtering |
| 11 - Evaluation | ⏳ Pending | Precision@K, Recall@K, MRR, Answer Relevancy |
| 12 - API & UI | ⏳ Pending | FastAPI REST endpoints + Streamlit UI |

---

## Quickstart

`ash
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

# 5. Run the Ingestion Pipeline
python -m src.ingestion.pipeline
`

---

## License

MIT License. For educational and portfolio use.
