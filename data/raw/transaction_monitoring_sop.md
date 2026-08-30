# Transaction Monitoring Standard Operating Procedure

## Purpose
This SOP defines the procedures for monitoring, detecting, and responding to suspicious transaction patterns across all payment channels.

## Scope
Applies to all transaction monitoring analysts, AML officers, and operations staff responsible for transaction surveillance.

## 1. Monitoring Systems
The bank uses three complementary systems for transaction monitoring:
- TMS (Transaction Monitoring System): Rule-based real-time alerts
- FRAML (Fraud and AML Platform): Machine learning-based anomaly detection
- SWIFT Sanctions Screening: Real-time sanctions list checking

## 2. Alert Categories

### 2.1 Priority 1 - Critical Alerts (Response within 30 minutes)
- Sanctions list match
- Terrorist financing indicator
- Large cash transaction above INR 10 lakh
- Structuring detected (multiple transactions just below threshold)
- Account takeover indicators
- Rapid succession of high-value transfers

### 2.2 Priority 2 - High Alerts (Response within 2 hours)
- PEP transaction above INR 5 lakh
- Unusual foreign currency transactions
- Wire transfers to high-risk jurisdictions
- Velocity spike: more than 20 transactions in 1 hour
- New account receiving large credit within 7 days of opening
- Round-dollar transactions pattern detected

### 2.3 Priority 3 - Medium Alerts (Response within 24 hours)
- Customer transaction deviates significantly from historical profile
- New payee receiving transfers above INR 1 lakh
- Multiple failed authentication attempts followed by successful login
- Dormant account suddenly active with large transactions
- Peer-to-peer transfer patterns inconsistent with profile

### 2.4 Priority 4 - Low Alerts (Response within 72 hours)
- Minor profile deviations
- Informational alerts for enhanced monitoring customers
- Periodic review triggers

## 3. Investigation Procedure

### Step 1: Alert Receipt and Triage
1. Log alert receipt time in case management system
2. Assign priority based on alert category
3. Assign to available analyst
4. Acknowledge alert within defined SLA

### Step 2: Initial Review (15 minutes)
1. Review customer profile: KYC data, risk rating, account history
2. Review transaction details: amount, counterparty, channel, time
3. Check customer against internal watchlists
4. Check counterparty against sanctions lists
5. Review recent account activity (last 90 days)

### Step 3: In-depth Investigation
1. Pull complete transaction history for relevant period
2. Identify pattern: frequency, amounts, counterparties
3. Review linked accounts and related customers
4. Check for open cases or prior SARs on customer
5. Assess against typology indicators
6. Document findings in case management system

### Step 4: Decision Making
Options available:
A. Clear the alert - document reasons clearly
B. Escalate for further review - provide preliminary findings
C. File Suspicious Activity Report (SAR) - complete SAR template
D. File Currency Transaction Report (CTR) - for cash transactions above threshold
E. Recommend account restriction or closure - escalate to senior AML officer
F. File STR with FIU-IND - for cases meeting STR criteria

### Step 5: Documentation Requirements
All cases must document:
- Alert details and source
- Customer and account information reviewed
- Transaction details analyzed
- External databases checked
- Rationale for decision
- Analyst name and timestamp
- Reviewer name and timestamp (for escalated cases)

## 4. Suspicious Transaction Report (STR) Filing

### 4.1 STR Criteria
File an STR when:
- Transaction has no apparent lawful purpose
- Transaction is inconsistent with customer profile
- Customer behavior is unusual or evasive
- Transaction involves known money laundering typologies
- There is reason to suspect proceeds of crime

### 4.2 STR Timeline
- Decision to file: Within 7 days of suspicion arising
- STR submission to FIU-IND: Within 7 days of decision
- STR acknowledgement from FIU-IND: Usually within 48 hours

### 4.3 Tipping Off Prohibition
Under PMLA 2002, it is illegal to inform the customer that an STR has been filed or that they are under investigation. Violators face criminal prosecution.

## 5. High-Risk Jurisdiction List
Transactions involving the following require enhanced scrutiny:
- FATF blacklisted countries
- Countries with EU or UN financial sanctions
- High-risk jurisdictions as per RBI guidelines (updated quarterly)
- Countries flagged by internal risk committee

## 6. Typology Reference

### 6.1 Structuring / Smurfing
Pattern: Multiple transactions just below reporting threshold (e.g., INR 9.5 lakh multiple times)
Action: File STR; check for coordination across accounts

### 6.2 Layering
Pattern: Rapid movement of funds through multiple accounts before withdrawal
Action: Map all accounts involved; freeze pending investigation

### 6.3 Trade-Based Money Laundering
Pattern: Import/export invoices that are over/under-valued; multiple invoicing
Action: Request trade documents; involve trade finance team

### 6.4 Account Takeover
Pattern: Password reset followed by immediate large transfer to new beneficiary
Action: Freeze transaction; contact customer through verified channel; file incident report

### 6.5 Mule Account
Pattern: Account receives credits and immediately forwards to other accounts; customer does not use account for personal expenses
Action: Restrict account; investigate source and destination; file STR

## 7. Escalation and Reporting

### 7.1 Internal Escalation
- Analyst to Senior Analyst: Cases requiring expert judgment
- Senior Analyst to AML Manager: STR filings; account restrictions
- AML Manager to Chief Compliance Officer: High-profile cases; regulatory inquiries
- CCO to Board Risk Committee: Quarterly AML report; significant cases

### 7.2 Regulatory Reporting Schedule
- STR filing: Within 7 days as per PMLA
- CTR filing: Monthly summary by 15th of following month
- KYC risk classification report: Quarterly
- AML program effectiveness report: Annual
