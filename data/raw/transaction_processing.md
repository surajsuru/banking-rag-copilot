# Transaction Processing Operating Model

Version 4.2 | Owner: Payments Platform

## Stages
1. Validate request.
2. Authenticate and authorize.
3. Validate account and limits.
4. Reserve funds.
5. Submit to rail or transfer engine.
6. Receive rail/switch result.
7. Post accounting entries.
8. Emit events.
9. Reconcile async confirmations.

## State distinction
SWITCH_SUCCESS means the external component accepted the instruction. LEDGER_POSTED means the core ledger recorded the accounting entry. They are not interchangeable.

## Version 4.2 timeout
Gateway timeout -> PENDING_EXTERNAL_RESULT. Do not immediately create a customer-visible terminal failure unless a policy explicitly says the request is terminal.

## Older behavior
Version 4.0 mapped some gateway timeouts directly to FAILED.

## Errors
TXN-1001 invalid account state; TXN-1042 beneficiary validation incomplete; TXN-2031 ledger posting unavailable; GW-3007 external switch timeout.
