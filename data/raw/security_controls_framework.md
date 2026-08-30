# Enterprise Information Security & Access Controls Framework

## 1. Governance & Compliance Frameworks
This security framework enforces mandatory compliance with:
- RBI Cyber Security Framework for Banks
- PCI-DSS v4.0 (Payment Card Industry Data Security Standard)
- ISO/IEC 27001:2022 Information Security Management
- Digital Personal Data Protection Act (DPDPA) 2023

## 2. Identity and Access Management (IAM)

### 2.1 Role-Based Access Control (RBAC) Hierarchy
Access to customer records, transaction payloads, and retrieval indexes is restricted strictly by role:

| Role Name | Description | Permissions | Data Masking Level |
|---|---|---|---|
| VIEWER | Read-only general documentation | Read public docs, SOPs | Full Masking (no PII) |
| SUPPORT_AGENT | Tier 1 Customer Support | Read customer tickets, view transaction status | Masked PII (First 2 / Last 4 digits) |
| OPERATIONS_ENGINEER| Payment Operations & Investigations | Initiate reversals, read raw logs, manage breaks | Partial Masking |
| DEVELOPER | Software Engineering & QA | Deploy services, read non-prod logs, test APIs | Synthetic Test Data Only |
| COMPLIANCE_OFFICER| AML, KYC & Legal audits | Full access to audit trails, STR reports, PEP flags | Unmasked with audit trail |
| ADMIN | System Administrators | User provisioning, key rotation, security config | Restricted operational view |

### 2.2 Multi-Factor Authentication (MFA) & Zero Trust
- All internal portal and administrative sessions enforce Hardware FIDO2 Security Keys or TOTP authenticator. SMS OTP is prohibited for administrative privilege elevation.
- Zero Trust Network Architecture (ZTNA): Access to internal endpoints requires device posture assessment, client certificate validation, and short-lived session tokens.

## 3. Data Protection, Cryptography & Masking

### 3.1 Encryption Standards
- **Data in Transit**: TLS 1.3 mandatory across all public and intra-service communication with strict cipher suites (ECDHE-ECDSA-AES256-GCM-SHA384). TLS 1.0/1.1 disabled.
- **Data at Rest**: AES-256-GCM encryption for database tables, vector index embeddings, and persistent volume disks.
- **Key Management**: Keys managed via dedicated Hardware Security Module (HSM) with annual automatic rotation.

### 3.2 Sensitive Data Masking Rules (PII / Cardholder Data)
- **Primary Account Number (PAN)**: Mask middle digits (e.g., 4532-XXXX-XXXX-8901).
- **Aadhaar Number**: Mask first 8 digits (e.g., XXXX-XXXX-1234).
- **CVV / PIN / Passwords**: NEVER stored in raw, encrypted, or loggable formats. Discarded immediately after HSM packet construction.

## 4. Threat Detection & Security Incident Response
- Centralized SIEM & SOC monitoring with 24/7 automated alert correlation.
- Automated rate limiting and Web Application Firewall (WAF) blocking for SQLi, XSS, and SSRF attacks.
- Annual third-party penetration testing and continuous vulnerability scanning.
