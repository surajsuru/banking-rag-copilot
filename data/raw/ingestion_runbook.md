# Ingestion Runbook

## File routing
PDF -> preserve page boundaries. DOCX -> preserve headings and table text. Markdown/HTML -> preserve headings/lists. CSV -> attach headers to rows. JSON/NDJSON/YAML -> preserve field names and structural relationships. TXT -> preserve line order and timestamps.

## Canonical record
```json
{"document_id":"DOC-020","version":"8.5","source":"error_code_reference.pdf","access_level":"operations"}
```

## De-duplication
Use a content hash plus document_id/version/effective dates. Do not delete older versions blindly; temporal retrieval is part of the benchmark.

## Deterministic chunk IDs
DOC-020:v8.5:p03:chunk007

## Re-ingestion
1. Store new version.
2. Mark old chunks inactive.
3. Re-embed changed chunks.
4. Run regression tests.
5. Publish only after evaluation passes.
