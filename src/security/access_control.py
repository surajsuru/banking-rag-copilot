"""
access_control.py

Phase 10 - Role-Based Access Control (RBAC).

Banking systems require strict document-level access controls.
Not every employee should be able to query every document.

ROLES defined in this system:
-------------------------------
    public      → Unauthenticated or general-purpose access
                  Can only see publicly available documents (FAQs, public guides)

    agent       → Customer support / call centre agent
                  Sees public + operational-level documents
                  (reversal SOPs, IMPS guides, error codes)

    operations  → Back-office operations team
                  Sees public + operations + internal documents
                  (reconciliation, incident runbooks, release notes)

    compliance  → Compliance, risk, and audit team
                  Sees everything except admin-only documents
                  (KYC/AML policies, data retention, audit guides)

    admin       → Full unrestricted access to ALL documents

ACCESS LEVELS defined on each chunk:
--------------------------------------
    public      → Safe to share with anyone
    operations  → Visible to operations team and above
    internal    → Visible to compliance team and above
    confidential→ Visible to admin only

RBAC HIERARCHY (each role inherits lower levels):
    admin       → [public, operations, internal, confidential]
    compliance  → [public, operations, internal]
    operations  → [public, operations]
    agent       → [public, operations]
    public      → [public]
"""

from typing import List
from src.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Access Level Definitions
# ─────────────────────────────────────────────────────────────────────────────

# All valid access levels that can be assigned to a chunk
ALL_ACCESS_LEVELS = ["public", "operations", "internal", "confidential"]

# All valid user roles
ALL_ROLES = ["public", "agent", "operations", "compliance", "admin"]

# Maps each role → the set of access levels it is permitted to see
ROLE_PERMISSIONS: dict = {
    "public":     ["public"],
    "agent":      ["public", "operations"],
    "operations": ["public", "operations"],
    "compliance": ["public", "operations", "internal"],
    "admin":      ["public", "operations", "internal", "confidential"],
}


# ─────────────────────────────────────────────────────────────────────────────
# Core RBAC Function
# ─────────────────────────────────────────────────────────────────────────────

def get_allowed_access_levels(role: str) -> List[str]:
    """
    Returns the list of document access levels a given role is permitted to see.

    This list is passed directly to the SQL WHERE clause in vector and BM25
    search to filter out unauthorized chunks BEFORE they are ranked or returned.

    Args:
        role: The user's role string. Must be one of ALL_ROLES.
               Falls back to 'public' if the role is unrecognized.

    Returns:
        List of access level strings the role is authorized to retrieve.

    Examples:
        >>> get_allowed_access_levels("admin")
        ['public', 'operations', 'internal', 'confidential']

        >>> get_allowed_access_levels("agent")
        ['public', 'operations']

        >>> get_allowed_access_levels("unknown_role")
        ['public']   # Safe default — deny unknown roles
    """
    if role not in ROLE_PERMISSIONS:
        logger.warning(
            f"Unknown role '{role}' — defaulting to 'public' access only. "
            f"Valid roles: {ALL_ROLES}"
        )
        return ["public"]

    allowed = ROLE_PERMISSIONS[role]
    logger.info(f"Role '{role}' granted access levels: {allowed}")
    return allowed


def is_valid_role(role: str) -> bool:
    """
    Checks if the given role string is a recognized role.

    Args:
        role: The role string to validate.

    Returns:
        True if the role is valid, False otherwise.
    """
    return role in ALL_ROLES
