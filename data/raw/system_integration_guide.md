# Core Banking System Integration & Architecture Guide

## 1. High-Level Architecture Overview
The Banking Platform operates as an event-driven, hybrid cloud architecture connecting modern digital touchpoints with legacy Core Banking Systems (CBS) and payment switches.

### Architecture Topology
`
[ Web / Mobile Clients ] ──▶ [ API Gateway (Kong / Envoy) ]
                                      │
                                      ▼
                        [ Microservices Layer (Kubernetes) ]
                        - Account Service
                        - Payment Orchestrator
                        - Fraud & AML Engine
                        - RAG Knowledge Copilot
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
         [ Kafka Event Streaming ]           [ Integration Middleware (ESB) ]
                    │                                   │
                    ▼                                   ▼
       [ Data Lake / Vector DB ]             [ Core Banking System (Finacle/ISO 8583) ]
`

## 2. Core Banking Connectivity Protocols

### 2.1 ISO 8583 / ISO 20022 Financial Messaging
- Real-time card and payment switch messages utilize ISO 8583 (0100 Authorization Request, 0200 Financial Transaction Request, 0420 Reversal Advice).
- Interbank messaging modernizes to ISO 20022 XML formats (pacs.008 customer credit transfer, pacs.004 payment return, camt.053 bank-to-customer statement).

### 2.2 Integration Middleware & Connectors
- **Direct TCP/IP Sockets**: For low-latency switch connections with bitmap parsing.
- **IBM MQ / JMS**: For guaranteed delivery of batch transactions to mainframe and CBS backends.
- **gRPC Services**: For internal high-throughput service-to-service communication with protobuf schemas.
- **RESTful JSON**: For customer-facing public APIs secured by OAuth 2.0 / mTLS.

## 3. Resilience, High Availability & Disaster Recovery (DR)

### 3.1 RPO & RTO Objectives
- **Recovery Point Objective (RPO)**: 0 seconds (zero data loss for financial ledgers via synchronous replication).
- **Recovery Time Objective (RTO)**: < 15 minutes for total primary datacenter failure with automated DNS/BGP route shifting.

### 3.2 Circuit Breakers & Backpressure Handling
All external outbound integrations must encapsulate calls within resilience patterns:
- Failure rate threshold: 50% failures over 10-second rolling window triggers OPEN state.
- Half-open retry interval: 15 seconds with single canary probe.
- Fallback actions: Return cached read models or queue asynchronous offline processing requests.

## 4. Idempotency Key Specification
To prevent duplicate debits from network retries, all mutate endpoints (POST /payments, POST /transfers) require an Idempotency-Key HTTP header (UUIDv4).
- Idempotency record stored in Redis with 24-hour TTL.
- If identical key is received while prior request is still executing: return HTTP 409 Conflict.
- If identical key is received after successful execution: return exact cached response with X-Cache-Lookup: HIT.
