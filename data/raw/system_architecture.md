# Banking Operations Copilot - Reference Architecture

## Runtime
User -> API -> Authentication -> Query Rewrite -> Access Filter -> Hybrid Retriever -> Reranker -> Prompt Builder -> LLM -> Citation Builder -> Audit Log

## Ingestion
Files -> Type Router -> Text/Structure Extraction -> Cleaning -> Chunking -> Metadata Enrichment -> Embedding -> Vector Store

## Metadata
document_id, filename, format, domain, access_level, version, section, page, chunk_id, effective_from, effective_to, source_type

## Retrieval policy
1. Apply authorization before exposing evidence.
2. Run semantic and keyword retrieval.
3. Merge and rerank candidates.
4. Pass only the best evidence to the model.
5. Require citations.
6. Abstain when evidence is insufficient.

## Failure modes
- Wrong version retrieved
- Exact error code outranked by generic content
- Unauthorized chunk retrieved
- Table header separated from values
- Log timestamps dropped
- Conflicting evidence
- Question not answerable from corpus
