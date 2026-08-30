# NexusCore API Authentication Guide

Version 3.0 | Owner: Platform Engineering

## Scopes
- GET /v1/accounts/{id} -> account.read
- GET /v1/accounts/{id}/balance -> account.read
- POST /v1/transactions -> transaction.write
- POST /v1/transactions/{id}/reverse -> transaction.reverse

## Authentication vs authorization
Authentication answers who is calling. Authorization answers what that caller may do.

## Errors
401 AUTH-401 = invalid/missing credential.
403 AUTH-403 = valid credential but missing required scope.
429 AUTH-429 = rate limit exceeded.

## Rules
Never put bearer tokens in URLs. Never log raw Authorization headers. Never treat a 2xx gateway response as proof that ledger posting completed.
