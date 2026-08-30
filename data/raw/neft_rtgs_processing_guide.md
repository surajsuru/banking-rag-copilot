# NEFT and RTGS Payment Processing Guide

## Overview
This guide covers the complete processing workflow for National Electronic Funds Transfer (NEFT) and Real Time Gross Settlement (RTGS) payment systems used within the banking platform.

## 1. NEFT Processing

### 1.1 What is NEFT
NEFT (National Electronic Funds Transfer) is a nation-wide payment system facilitating one-to-one funds transfer. Under this Scheme, individuals, firms and corporates can electronically transfer funds from any bank branch to any individual, firm or corporate having an account with any other bank branch in the country participating in the Scheme.

### 1.2 NEFT Settlement Cycles
NEFT operates in half-hourly batches. There are 23 settlements from 8:00 AM to 7:00 PM on weekdays.
- Settlement Batch 1: 08:00 AM
- Settlement Batch 2: 08:30 AM
- Settlement Batch 3: 09:00 AM
- Settlement Batch 4: 09:30 AM
- Settlement Batch 5: 10:00 AM
- Settlement Batch 6: 10:30 AM
- Settlement Batch 7: 11:00 AM
- Settlement Batch 8: 11:30 AM
- Settlement Batch 9: 12:00 PM
- Settlement Batch 10: 12:30 PM
- Settlement Batch 11: 01:00 PM
- Settlement Batch 12: 01:30 PM
- Settlement Batch 13: 02:00 PM
- Settlement Batch 14: 02:30 PM
- Settlement Batch 15: 03:00 PM
- Settlement Batch 16: 03:30 PM
- Settlement Batch 17: 04:00 PM
- Settlement Batch 18: 04:30 PM
- Settlement Batch 19: 05:00 PM
- Settlement Batch 20: 05:30 PM
- Settlement Batch 21: 06:00 PM
- Settlement Batch 22: 06:30 PM
- Settlement Batch 23: 07:00 PM

NEFT is available 24x7 including weekends and holidays as per RBI guidelines effective December 2019.

### 1.3 NEFT Transaction Limits
- Minimum amount: No minimum limit
- Maximum amount: No upper ceiling for NEFT transfers
- However, individual banks may set their own limits for retail customers
- Corporate customers: Up to INR 10,00,00,000 per transaction (configurable)

### 1.4 NEFT Processing Flow
Step 1 - Originating Bank: The remitter initiates the NEFT request at the originating bank branch or through internet banking.
Step 2 - Message Preparation: The originating bank prepares the NEFT message in the prescribed format and transmits to its pooling centre.
Step 3 - Pooling Centre: The pooling centre consolidates messages from all branches and forwards to NEFT Service Centre.
Step 4 - RBI NEFT Service Centre: The service centre sorts the transactions bank-wise and prepares accounting entries.
Step 5 - Settlement: RBI debits the sending bank and credits the receiving bank through their accounts maintained at RBI.
Step 6 - Destination Bank: The destination bank receives the credit entry and credits the beneficiary account.
Step 7 - Confirmation: Transaction confirmation is sent back to the originating bank and ultimately to the remitter.

### 1.5 NEFT Return Processing
Transactions may be returned for the following reasons:
- Account closed (Return Code: R01)
- No such account (Return Code: R02)
- Account frozen (Return Code: R03)
- Invalid account type (Return Code: R04)
- Amount not matching (Return Code: R05)
- Beneficiary deceased (Return Code: R06)
- Account blocked by court order (Return Code: R07)
- Credit not accepted by beneficiary (Return Code: R08)

Return transactions must be processed within 2 hours of receipt of the return message.

### 1.6 NEFT Charges
As per RBI guidelines effective January 2020, banks are not permitted to charge customers for NEFT transactions initiated online. For branch-initiated transactions, charges may apply as per individual bank policy.

## 2. RTGS Processing

### 2.1 What is RTGS
RTGS (Real Time Gross Settlement) is a funds transfer mechanism where transfer of money takes place from one bank to another on a real time and on gross basis. Settlement in real time means payment transaction is not subjected to any waiting period.

### 2.2 RTGS Operating Hours
RTGS is available 24x7x365 as per RBI circular RBI/2020-21/62 dated December 2020.

### 2.3 RTGS Transaction Limits
- Minimum amount: INR 2,00,000 (Two Lakh Rupees)
- Maximum amount: No upper limit
- Corporate customers may have bank-defined upper limits

### 2.4 RTGS Processing Flow
Step 1 - Initiation: Remitter fills in the RTGS application form with beneficiary details.
Step 2 - Verification: Bank verifies the IFSC code and account details.
Step 3 - Message Transmission: Bank transmits the RTGS message to RBI RTGS system.
Step 4 - Real-time Settlement: RBI RTGS system checks the sending bank balance and processes the settlement immediately.
Step 5 - Credit Notification: RBI sends credit notification to the destination bank.
Step 6 - Beneficiary Credit: Destination bank credits the beneficiary account within 30 minutes of receiving the credit notification.
Step 7 - Acknowledgement: Sending bank receives acknowledgement and notifies the remitter.

### 2.5 RTGS Error Codes and Resolution
- RTGS-E001: Insufficient funds in sending bank account at RBI
  Resolution: Top up the settlement account and retry
- RTGS-E002: Invalid IFSC code
  Resolution: Verify IFSC code with the RBI IFSC directory
- RTGS-E003: Beneficiary account not found
  Resolution: Contact destination bank for account verification
- RTGS-E004: Message format error
  Resolution: Review message format against RTGS message specification v3.1
- RTGS-E005: Duplicate transaction reference
  Resolution: Generate new unique transaction reference
- RTGS-E006: Transaction amount below minimum threshold
  Resolution: RTGS minimum is INR 2 lakhs; use NEFT for smaller amounts
- RTGS-E007: Settlement account not available
  Resolution: Contact RBI RTGS helpdesk
- RTGS-E008: Bank not participating in RTGS
  Resolution: Verify bank participation status in RBI directory

### 2.6 RTGS Charges
As per RBI circular, RTGS charges have been waived for all customers with effect from 01 July 2019.

## 3. Common Processing Issues

### 3.1 Reconciliation Failures
If NEFT or RTGS transactions are not reflected in the reconciliation report:
1. Check the transaction status in the NEFT/RTGS monitoring system
2. Verify settlement account balance
3. Check RBI SFMS (Structured Financial Messaging System) logs
4. Contact RBI helpdesk if issue persists beyond 4 hours

### 3.2 Duplicate Transaction Handling
- All transactions must carry unique End-to-End IDs
- System performs duplicate check within 24-hour rolling window
- Suspected duplicates are flagged and held for manual review
- Operations team must approve or reject held transactions within 2 hours

### 3.3 Cut-off Time Management
- NEFT: Last batch at 7:00 PM; transactions received after cut-off processed in next available batch
- RTGS: 24x7 processing; no cut-off time
- Year-end and holiday processing: Refer to RBI circular for specific dates

### 3.4 Transaction Monitoring Thresholds
- NEFT transactions above INR 10,00,000: Flagged for AML review
- RTGS transactions above INR 50,00,000: Mandatory maker-checker approval
- Cross-border equivalent transactions: FEMA compliance check mandatory

## 4. Operational Procedures

### 4.1 Daily Reconciliation Steps
1. Download EOD NEFT settlement report from RBI portal
2. Match with internal core banking system entries
3. Identify and escalate unmatched entries (threshold: INR 1,000)
4. Generate reconciliation certificate by 11:00 PM daily
5. Submit to Finance team for sign-off

### 4.2 Escalation Matrix
Level 1: Operations Executive - Response time 30 minutes
Level 2: Operations Manager - Response time 1 hour
Level 3: Head of Payments - Response time 2 hours
Level 4: CTO/CFO - Response time 4 hours (critical issues only)

### 4.3 SLA Commitments
- NEFT credit to beneficiary: Within 2 hours of settlement
- RTGS credit to beneficiary: Within 30 minutes of RBI credit notification
- Return processing: Within 2 hours of return receipt
- Reconciliation completion: By 11:00 PM daily

## 5. Regulatory Compliance

### 5.1 RBI Reporting
All NEFT and RTGS transactions are reported to RBI through:
- SFMS (Structured Financial Messaging System) daily reports
- RTGS Real-time monitoring dashboard
- Monthly statistical returns

### 5.2 AML Obligations
Transactions triggering AML thresholds must be:
1. Reported to the AML system within 2 hours
2. Reviewed by the Compliance team within 24 hours
3. Filed as Suspicious Transaction Report (STR) if required within 7 days
4. Escalated to FIU-IND as applicable

### 5.3 Record Keeping
All NEFT and RTGS transaction records must be maintained for:
- Operational records: 7 years
- AML-related records: 10 years
- Regulatory correspondence: 5 years
