# End-of-Day Payment Reconciliation & Settlement Procedures

## 1. Objectives & Scope
This document specifies daily end-of-day (EOD) financial reconciliation, dispute settlement, and discrepancy accounting procedures across multi-rail payment ecosystems (UPI, IMPS, NEFT, RTGS, Card Networks).

## 2. The 3-Way Reconciliation Architecture
Reconciliation ensures mathematical parity among three distinct ledgers:

`
[ Internal Core Banking Ledger (CBS) ]
                  ▲
                  │  (2-way comparison)
                  ▼
[ Switch / Gateway Transaction Journal ]
                  ▲
                  │  (3-way clearing)
                  ▼
[ Settlement File from Clearing House (NPCI / RBI / Card Switch) ]
`

### 2.1 File Ingestion Timelines
- **NPCI UPI Settlement (EP File)**: Ingested at 06:00, 11:30, 15:30, 19:30, and 23:30 IST.
- **RBI NEFT/RTGS Daily Settlement File**: Available at 23:45 IST via SFMS gateway.
- **Visa/Mastercard Clearing Files (Base II / IPM)**: Ingested at 02:00 IST for previous business day.
- **Internal CBS Snapshot**: Generated at 23:59:59 IST daily cutoff.

## 3. Discrepancy Types & Settlement Actions

### 3.1 Type 1: Deemed Success (Customer Debited, Gateway Success, Beneficiary Not Credited)
- **Root Cause**: Downstream timeout during final credit leg.
- **Resolution**: Auto-reversal or push credit within T+1 working days as per RBI Harmonization Circular.
- **Penalty for Delay**: Compensation of INR 100 per day payable to customer if delayed beyond T+1 days.

### 3.2 Type 2: Force Debit / Chargeback (Customer Credited, Gateway Failed)
- **Root Cause**: Late arrival of confirmation message after timeout reversal.
- **Resolution**: Post adjusting entry to General Ledger (GL) account GL-SUSPENSE-SETTLE-092. File representative request to clearing house.

### 3.3 Type 3: Fee and Surcharge Mismatch
- **Root Cause**: Interchange rate tier miscalculation or tax rounding variance.
- **Resolution**: Daily tolerance threshold is INR 500 across batch. Variances above threshold are flagged for manual auditor review.

## 4. Operational Reconciliation Step-by-Step Runbook
1. **Trigger Ingestion Job**: Run python -m src.reconciliation.engine --date=YYYY-MM-DD.
2. **Review Auto-Match Score**: Check summary metric. Expected automated match rate: >= 99.85%.
3. **Inspect Break Queue**: Any record with status UNMATCHED_AMOUNT, MISSING_INTERNAL, or MISSING_EXTERNAL is routed to the Exception Management Portal.
4. **Post Settlement Journal Voucher (JV)**:
   - Debit: Clearing Settlement Account (RBI/NPCI)
   - Credit: Customer Pool / Merchant Settlement Account
   - Difference: Operational Suspense GL
5. **Sign-off**: Senior Operations Manager reviews variance sheet and signs the daily EOD balancing certificate.

## 5. Audit & Regulatory Archive Mandates
- Daily reconciliation logs, raw clearing files, and dispute vouchers must be digitally signed with SHA-256 hashes and archived in WORM (Write Once Read Many) compliant storage for a minimum of 8 years.
