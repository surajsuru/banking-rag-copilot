# Chunking Benchmark Notes

## Candidate strategies
A. Fixed token chunks: 350-600 tokens with 50-80 overlap.
B. Heading-aware chunks: keep headings, paragraphs, lists and adjacent tables together.
C. Semantic chunks: chunk by process, error code, API operation, or policy control.

## Benchmark queries
- TXN-1042
- What should happen after a debit succeeds but the beneficiary credit times out?
- Which API returns availableBalance?
- Who can approve an emergency production change?
- What evidence is required for KYC remediation?

## Expected observations
Exact identifiers tend to benefit from keyword retrieval. Process questions tend to benefit from semantic retrieval. Tables and structured records require preserving row/field context.
