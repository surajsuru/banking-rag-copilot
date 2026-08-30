# Banking Platform Release Notes — v2.0 to v3.2 Migration & Changelog

## 1. Release Overview
This document tracks major architectural upgrades, API breaking changes, schema evolutions, and deprecated endpoints between Platform Release v2.0 (Legacy) and Release v3.2 (Current Enterprise Core).

---

## Release v3.2.0 (Current Stable — Q1 2026)
### Major Features & Enhancements
- **Multi-Rail Instant Settlement Engine**: Native orchestration across UPI 2.0, IMPS 24x7, and new RTGS real-time settlement APIs.
- **Enhanced Vector RAG Knowledge Copilot Integration**: Internal operations assist tool for accelerated support ticket triage and error code resolution.
- **Zero-Downtime Database Schema Migrations**: Introduced blue-green database deployment pipelines.

### API Changes
- Added /v3/payments/upi/collect with support for mandated recurring UPI autopay collections.
- Added /v3/transactions/bulk supporting asynchronous streaming uploads of up to 10,000 items.

---

## Release v3.1.0 (Q3 2025)
### Major Features
- **ISO 20022 Message Gateway**: Full support for XML pacs.008 and camt.053 message translation for interbank transfers.
- **Automated 3-Way Reconciliation Pipeline**: Reduced manual EOD reconciliation exceptions by 84%.

### Security Updates
- Upgraded mTLS certificate authorities and implemented OAuth 2.0 DPoP (Demonstrating Proof-of-Possession) token security.

---

## Release v3.0.0 (Major Architectural Overhaul — Q1 2025)
### ⚠️ Breaking Changes & Deprecations
- **Authentication**: Deprecated legacy Basic Auth and static API keys in query parameters. All clients must use /v3/auth/token OAuth 2.0 Bearer tokens.
- **Account Number Format**: Standardized internal account identifiers to global prefix format (ACC- + 10 digits).
- **Error Response Contract**: Replaced unstructured plain-text error messages with standardized RFC 7807 problem details JSON format (errorCode, errorMessage, correlationId).

### Migration Guide from v2 to v3
1. Update API base URL from https://api.bank.internal/v2 to https://api.bank.internal/v3.
2. Replace static header X-API-KEY: <key> with Authorization: Bearer <jwt_token>.
3. Update webhook signature verification algorithm from MD5 hash to HMAC-SHA256 with timestamp validation.
4. Legacy v2 endpoints will return HTTP 410 Gone after December 31, 2026.
