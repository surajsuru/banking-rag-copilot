"""
tag_access_levels.py

Phase 10 - RBAC Document Tagging Script.

Assigns an access_level to every chunk in the database based on its source_file.

Access Level Rules:
    confidential → Highly sensitive internal documents (access matrix, pricing)
    internal     → Compliance, audit, KYC/AML, data retention policies
    operations   → Operational runbooks, SOPs, IMPS/NEFT guides, incident logs
    public       → Everything else (FAQs, public-facing guides, API docs)

Run once after migrate_access_level.py has been executed.
"""

from src.database.vector_store import connect
from src.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Document → Access Level Mapping
# Add any new documents here as the knowledge base grows.
# ─────────────────────────────────────────────────────────────────────────────

# Chunks from these files are CONFIDENTIAL (admin-only)
CONFIDENTIAL_DOCS = {
    "access_matrix.csv",
    "product_pricing_matrix.csv",
}

# Chunks from these files are INTERNAL (compliance + above)
INTERNAL_DOCS = {
    "kyc_aml_manual.md",
    "kyc_policy.pdf",
    "data_retention_policy.html",
    "change_management_policy.html",
    "security_framework.md",
    "architecture_guide.md",
}

# Chunks from these files are OPERATIONS (operations team + above)
OPERATIONS_DOCS = {
    "transaction_reversal_sop.docx",
    "imps_operations_guide.pdf",
    "incident_runbook.docx",
    "incident_playbook.md",
    "incident_logs.txt",
    "payment_reconciliation.pdf",
    "neft_rtgs_guide.md",
    "release_notes.docx",
    "release_notes_v2.md",
    "release_notes_v3.md",
    "error_codes_manual.md",
    "error_code_reference.pdf",
    "event_schema.ndjson",
    "support_tickets.json",
}

# Everything else defaults to PUBLIC


def classify_access_level(source_file: str) -> str:
    """
    Returns the access level for a given source filename.

    Args:
        source_file: The filename of the document (e.g. 'kyc_policy.pdf').

    Returns:
        One of: 'confidential', 'internal', 'operations', 'public'
    """
    if source_file in CONFIDENTIAL_DOCS:
        return "confidential"
    if source_file in INTERNAL_DOCS:
        return "internal"
    if source_file in OPERATIONS_DOCS:
        return "operations"
    return "public"


def tag_all_chunks():
    """
    Updates the access_level of every chunk in the database
    based on its source_file.
    """
    conn = connect()
    cur = conn.cursor()

    # Fetch all distinct source files
    cur.execute("SELECT DISTINCT source_file FROM chunks ORDER BY source_file;")
    source_files = [row[0] for row in cur.fetchall()]
    logger.info(f"Found {len(source_files)} distinct source files to tag.")

    counts = {"public": 0, "operations": 0, "internal": 0, "confidential": 0}

    for source_file in source_files:
        level = classify_access_level(source_file)
        cur.execute(
            "UPDATE chunks SET access_level = %s WHERE source_file = %s;",
            (level, source_file)
        )
        rows_updated = cur.rowcount
        counts[level] += rows_updated
        logger.info(f"  [{level:>12}]  {source_file}  ({rows_updated} chunks)")

    conn.commit()

    print("\n" + "=" * 60)
    print("ACCESS LEVEL TAGGING COMPLETE")
    print("=" * 60)
    for level, count in counts.items():
        print(f"  {level:>12} : {count} chunks")
    print(f"  {'TOTAL':>12} : {sum(counts.values())} chunks")
    print("=" * 60)

    cur.close()
    conn.close()


if __name__ == "__main__":
    tag_all_chunks()
