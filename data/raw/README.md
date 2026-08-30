# Banking Enterprise Knowledge & Operations Copilot - RAG Corpus

Generated: 2026-08-30

This is a **synthetic enterprise banking corpus** for learning Retrieval-Augmented Generation. It is designed to behave like the knowledge base of a banking technology company, without using proprietary Finacle manuals or confidential bank material.

## Provenance
Most internal documents, APIs, error codes, incident records and policies are fictional. A small number of files deliberately use public banking concepts inspired by official RBI, NPCI and ISO 20022 references; see `source_register.md`.

## What the corpus contains
- Product and operations manuals
- API specifications and event schemas
- Compliance and digital-payment security documents
- Error-code reference and noisy incident logs
- Support FAQs and support tickets
- Versioned release notes and change-management policy
- Different access levels for role-based retrieval testing
- Structured CSV/JSON/YAML plus semi-structured DOCX/PDF/HTML/TXT/MD

## Suggested learning path
1. Parse and normalize every format.
2. Chunk while preserving headings, pages, tables and field names.
3. Embed and store in pgvector.
4. Test semantic retrieval.
5. Add BM25/keyword retrieval.
6. Add metadata access filtering.
7. Add reranking and citations.
8. Evaluate with `evaluation_questions.json`.
