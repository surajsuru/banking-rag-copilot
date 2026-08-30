# API Integration Handbook

## Version 3.2 | Banking Platform API Documentation

## 1. Introduction

This handbook provides comprehensive documentation for integrating with the Banking Platform APIs. All integrations must comply with PCI-DSS, RBI guidelines, and internal security policies.

### 1.1 Base URLs
- Production: https://api.bankingplatform.internal/v3
- Staging: https://api-staging.bankingplatform.internal/v3
- Sandbox: https://api-sandbox.bankingplatform.internal/v3

### 1.2 API Versioning
APIs are versioned using URL path versioning. Current stable version: v3. Version v2 is deprecated and will be decommissioned on 31 December 2026. All clients must migrate to v3 by that date.

### 1.3 Authentication Methods
The platform supports three authentication methods:
1. OAuth 2.0 Client Credentials (recommended for server-to-server)
2. API Key + HMAC Signature (for legacy integrations)
3. Mutual TLS (for high-security integrations)

## 2. OAuth 2.0 Authentication

### 2.1 Obtaining Access Token
Endpoint: POST /auth/token
Content-Type: application/x-www-form-urlencoded

Request parameters:
- grant_type: client_credentials
- client_id: Your assigned client ID
- client_secret: Your client secret
- scope: Comma-separated list of requested scopes

Available scopes:
- accounts:read - Read account information
- accounts:write - Modify account information
- transactions:read - Read transaction history
- transactions:write - Initiate transactions
- payments:initiate - Initiate payment transactions
- payments:approve - Approve pending payments
- reports:read - Access reports and statements
- admin:read - Read administrative data (restricted)

Sample request:
POST /auth/token
Body: grant_type=client_credentials&client_id=CLT-12345&client_secret=secret&scope=transactions:read,payments:initiate

Sample response:
{
  access_token: eyJhbGciOiJSUzI1NiJ9...,
  token_type: Bearer,
  expires_in: 3600,
  scope: transactions:read payments:initiate
}

### 2.2 Token Refresh
Access tokens expire after 3600 seconds (1 hour). Request a new token using the same client credentials before the current token expires. Do not wait for a 401 error to refresh tokens.

### 2.3 Token Revocation
Endpoint: POST /auth/revoke
Revoke tokens when they are no longer needed or when a security incident occurs.

## 3. Account APIs

### 3.1 Get Account Details
Endpoint: GET /accounts/{accountId}
Required scope: accounts:read

Path parameters:
- accountId: The unique account identifier (format: ACC-XXXXXXXXXX)

Response fields:
- accountId: Unique account identifier
- accountNumber: Masked account number
- accountType: SAVINGS, CURRENT, FIXED_DEPOSIT, RECURRING_DEPOSIT
- currency: ISO 4217 currency code
- balance: Current balance
- availableBalance: Balance available for transactions
- status: ACTIVE, DORMANT, FROZEN, CLOSED
- customerId: Associated customer ID
- branchCode: Home branch IFSC code
- openedDate: Account opening date
- lastTransactionDate: Date of last transaction

### 3.2 Get Account Balance
Endpoint: GET /accounts/{accountId}/balance
Required scope: accounts:read

Returns real-time balance information including:
- currentBalance: Book balance
- availableBalance: Balance available after holds
- holdAmount: Total amount on hold
- lienAmount: Total lien amount

### 3.3 Get Account Statement
Endpoint: GET /accounts/{accountId}/statement
Required scope: accounts:read

Query parameters:
- fromDate: Start date (YYYY-MM-DD format)
- toDate: End date (YYYY-MM-DD format)
- page: Page number (default: 1)
- pageSize: Records per page (default: 50, max: 500)
- transactionType: DEBIT, CREDIT, ALL (default: ALL)

## 4. Transaction APIs

### 4.1 Initiate Fund Transfer
Endpoint: POST /transactions/transfer
Required scope: payments:initiate

Request body:
- sourceAccountId: Debiting account ID
- beneficiaryAccountNumber: Destination account number
- beneficiaryIFSC: Destination bank IFSC code
- beneficiaryName: Name of the beneficiary
- amount: Transfer amount (decimal, 2 decimal places)
- currency: ISO 4217 currency code (default: INR)
- transferMode: NEFT, RTGS, IMPS, UPI
- remarks: Transaction remarks (max 140 characters)
- referenceId: Client-generated unique reference (max 35 characters)
- scheduledDate: Optional. Date for future-dated transfer (YYYY-MM-DD)

Response:
- transactionId: Platform-assigned transaction ID
- referenceId: Echo of client reference ID
- status: INITIATED, PENDING_APPROVAL, PROCESSING, COMPLETED, FAILED
- estimatedSettlementTime: ISO 8601 timestamp
- charges: Array of applicable charges

### 4.2 Get Transaction Status
Endpoint: GET /transactions/{transactionId}
Required scope: transactions:read

Polling interval: Minimum 30 seconds between status checks.
Transaction terminal statuses: COMPLETED, FAILED, REVERSED, CANCELLED

### 4.3 Transaction Reversal
Endpoint: POST /transactions/{transactionId}/reverse
Required scope: payments:initiate

Reversal conditions:
- Transaction must be in COMPLETED status
- Reversal must be initiated within 24 hours of completion
- Reversal is subject to beneficiary bank cooperation for NEFT/RTGS

Request body:
- reason: Reason for reversal (DUPLICATE, ERROR, CUSTOMER_REQUEST, FRAUD)
- remarks: Additional remarks (max 140 characters)

### 4.4 Bulk Transaction Upload
Endpoint: POST /transactions/bulk
Required scope: payments:initiate

- Maximum 1000 transactions per batch
- File format: JSON array or CSV
- Async processing: returns batchId for status tracking
- Status webhook: Configure via /webhooks endpoint

## 5. Payment APIs

### 5.1 UPI Payment Initiation
Endpoint: POST /payments/upi/collect
Required scope: payments:initiate

Request body:
- payerVPA: Payer UPI Virtual Payment Address
- payeeVPA: Payee VPA
- amount: Payment amount
- remarks: Transaction remarks
- expiryMinutes: Request expiry in minutes (default: 10, max: 1440)

### 5.2 UPI VPA Validation
Endpoint: GET /payments/upi/validate/{vpa}
Required scope: payments:initiate

Validates if a VPA is registered and active in the UPI ecosystem.

### 5.3 IMPS Payment
Endpoint: POST /payments/imps
Required scope: payments:initiate

IMPS (Immediate Payment Service) enables 24x7 instant transfer.
- Available: 24x7x365
- Limit: Up to INR 5,00,000 per transaction
- Settlement: Real-time

## 6. Webhook Configuration

### 6.1 Registering Webhooks
Endpoint: POST /webhooks
Required scope: admin:read

Supported event types:
- transaction.completed
- transaction.failed
- transaction.reversed
- payment.received
- account.status.changed
- kyc.status.updated

Webhook payload includes:
- eventId: Unique event identifier
- eventType: Type of event
- timestamp: Event occurrence time
- data: Event-specific payload

### 6.2 Webhook Security
All webhook deliveries include an X-Signature header containing HMAC-SHA256 signature of the payload. Verify this signature before processing any webhook.

Verification algorithm:
1. Extract X-Signature header value
2. Compute HMAC-SHA256 of raw request body using your webhook secret
3. Compare computed signature with header value
4. Reject if they do not match

### 6.3 Webhook Retry Policy
Failed webhook deliveries are retried up to 5 times with exponential backoff:
- Attempt 1: Immediate
- Attempt 2: 5 minutes
- Attempt 3: 30 minutes
- Attempt 4: 2 hours
- Attempt 5: 12 hours

## 7. Rate Limits

### 7.1 Default Rate Limits
- Standard tier: 100 requests per minute
- Premium tier: 1000 requests per minute
- Bulk endpoints: 10 requests per minute

### 7.2 Rate Limit Headers
All API responses include:
- X-RateLimit-Limit: Requests allowed per window
- X-RateLimit-Remaining: Requests remaining in current window
- X-RateLimit-Reset: Unix timestamp when window resets

### 7.3 Rate Limit Exceeded Response
HTTP 429 Too Many Requests with Retry-After header indicating seconds to wait.

## 8. Error Handling

### 8.1 Standard Error Response Format
All errors return JSON with fields:
- errorCode: Application-specific error code (see Error Code Reference)
- errorMessage: Human-readable error description
- correlationId: Unique ID for tracing the request through logs
- timestamp: Error occurrence time
- details: Array of field-level validation errors (if applicable)

### 8.2 HTTP Status Code Mapping
- 200: Success
- 201: Resource created
- 400: Bad request - validation error
- 401: Unauthorized - authentication required
- 403: Forbidden - insufficient permissions
- 404: Resource not found
- 409: Conflict - duplicate resource
- 422: Unprocessable entity - business rule violation
- 429: Rate limit exceeded
- 500: Internal server error
- 503: Service unavailable

## 9. SDK and Client Libraries

Official client libraries are available for:
- Java (banking-api-client-java v3.2.0)
- Python (banking-api-client-python v3.2.0)
- Node.js (banking-api-client-node v3.2.0)
- .NET (BankingApiClient v3.2.0)

All SDKs are available on the internal artifact repository at https://nexus.internal/banking-sdks

## 10. Integration Checklist

Before going live, ensure:
1. IP whitelisting submitted to security team
2. Production credentials obtained from API portal
3. SSL/TLS certificate pinning implemented
4. Webhook signature verification implemented
5. Idempotency keys implemented for payment APIs
6. Retry logic with exponential backoff implemented
7. Rate limit handling implemented
8. Logging of all API requests and responses with correlation IDs
9. Security review completed by information security team
10. Load testing completed in staging environment
