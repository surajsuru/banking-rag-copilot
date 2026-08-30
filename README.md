# banking-rag-copilot

> An enterprise-grade Retrieval-Augmented Generation (RAG) system built from scratch for banking operations.

## What This Project Is

An AI-powered knowledge copilot for a banking company. Employees ask natural language questions about:
- Payment processing (UPI, NEFT, RTGS, IMPS)
- API documentation and integration guides
- Error codes and troubleshooting
- Transaction reversal procedures
- KYC / AML compliance policies
- Incident management runbooks
- Reconciliation procedures
- Security controls and access policies

The system retrieves relevant context from a knowledge base using RAG and generates grounded answers with citations.

---

## Why This Project Exists

Most RAG tutorials hide complexity behind LangChain/LlamaIndex. This project builds every component manually so you understand exactly what happens internally:

- How documents are loaded, parsed, cleaned
- How text is split into chunks and why chunk strategy matters
- How text becomes an embedding vector
- How vector similarity search works
- How hybrid retrieval combines semantic + keyword search
- How reranking improves result quality
- How access control is enforced at retrieval time
- How answers are grounded and cited

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Document Parsing | PyMuPDF, python-docx, BeautifulSoup4, PyYAML |
| Data Handling | pandas |
| Vector Database | PostgreSQL + pgvector |
| Embeddings | sentence-transformers |
| LLM | Configurable (OpenAI / local) |
| API | FastAPI |
| UI | Streamlit |

---

## Project Structure

`
banking-rag-copilot/
|
+-- data/
|   +-- raw/              # 40 synthetic banking documents (immutable source of truth)
|   +-- processed/        # Extracted, cleaned, chunked artifacts
|   +-- evaluation/       # Evaluation datasets and benchmark results
|
+-- src/
|   +-- ingestion/        # File discovery, parsing, cleaning, chunking
|   +-- embeddings/       # Embedding model and vector generation
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
+-- config.py
+-- requirements.txt
+-- docker-compose.yml
`

---

## Knowledge Base

40 synthetic banking documents across 9 formats: PDF, DOCX, Markdown, TXT, CSV, JSON, NDJSON, YAML, HTML.

Topics: UPI/NEFT/RTGS processing, API specs, 100+ error codes, KYC/AML policy, incident management, reconciliation, security controls, release notes.

> data/raw/ is immutable. Never modify files inside it.

---

## Development Phases

| Phase | Status | Description |
|---|---|---|
| 1 - Foundation | Done | Project structure, venv, config, logging |
| 2 - Ingestion | In Progress | Loader, parser (9 formats), cleaner |
| 3 - Chunking | Pending | Fixed, token-based, heading-aware |
| 4 - Embeddings | Pending | Embedding model, vector generation |
| 5 - Vector Storage | Pending | PostgreSQL + pgvector |
| 6 - Naive RAG | Pending | First end-to-end pipeline |
| 7 - Citations | Pending | Source tracking and grounded answers |
| 8 - Hybrid Retrieval | Pending | BM25 + vector search |
| 9 - Reranking | Pending | Cross-encoder reranking |
| 10 - Access Control | Pending | Role-based document filtering |
| 11 - Evaluation | Pending | Retrieval and generation metrics |
| 12 - API and UI | Pending | FastAPI + Streamlit |

---

## Setup

`ash
git clone https://github.com/YOUR_USERNAME/banking-rag-copilot.git
cd banking-rag-copilot
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
`

---

## Data Notice

All documents in data/raw/ are synthetic, created for learning purposes only.
They do not represent actual proprietary banking documentation.

---

## License

MIT License. For educational and portfolio use only.
