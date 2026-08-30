# Incident Management Playbook & Response Runbook

## Version 4.0 | Core Operations & Engineering Runbook

## 1. Overview & Severity Definitions
This playbook outlines standard operating procedures for identifying, triaging, mitigating, and resolving system outages, security events, and payment pipeline degradations.

### 1.1 Severity Classification Matrix
- **SEV-1 (Critical Outage)**: Complete downtime of primary payment gateways (UPI, IMPS, NEFT), Core Banking System (CBS) unresponsive, or verified data breach. Immediate pageout to executive leadership and war room creation within 5 minutes. SLA to resolve/workaround: 1 hour.
- **SEV-2 (Major Degradation)**: Partial disruption where a secondary channel is impaired, API error rates exceed 5%, or batch settlement delayed by > 30 minutes. SLA to mitigate: 2 hours.
- **SEV-3 (Minor Incident)**: Non-customer facing internal tool failure, single node flapping in redundant cluster, non-critical reporting pipeline lag. SLA: 8 business hours.
- **SEV-4 (Low / Informational)**: Minor UI cosmetic defect, transient alert self-healed, documentation discrepancy. SLA: Next sprint.

## 2. On-Call Escalation Matrix & Roles
- **Incident Commander (IC)**: Owns communication, delegates tasks, and maintains incident timeline. Does not write code during the incident.
- **Technical Lead (TL)**: Coordinates debugging, infrastructure scaling, hotfix deployments.
- **Communications Lead**: Updates status dashboards (status.bank.internal), informs customer support, and briefs executive sponsors.
- **Operations Liaison**: Interfaces with clearing houses (NPCI, RBI) and settlement partner banks.

## 3. Standard Incident Response Workflow
`
[Detection / PagerDuty Alert]
            │
            ▼
[Triage & Severity Assignment (0-5 min)]
            │
            ▼
[War Room Activation & Incident Commander Assignment]
            │
            ▼
[Root Cause Containment & Rollback / Failover Strategy]
            │
            ▼
[Verification & Metric Stabilization]
            │
            ▼
[Post-Mortem & Corrective Action Item (CAPA) Filing (within 48h)]
`

## 4. Runbooks for Specific Failure Scenarios

### 4.1 Payment Gateway Switch Failure (UPI/IMPS)
1. Check synthetic health check probe results across switch endpoints.
2. If primary switch returns 502/504 errors for > 2 minutes, trigger automatic circuit breaker.
3. Switch routing engine config to backup PSP partner switch:
   kubectl exec -it switch-router -- ./failover.sh --partner=SECONDARY_PSP --force
4. Notify NPCI NOC of route switch via emergency hotline.
5. Monitor real-time transaction success rate (TSR) in Grafana dashboard Payments-Executive-Overview.
6. Target TSR recovery: > 92% within 10 minutes.

### 4.2 Core Banking Database Deadlocks / Connection Pool Exhaustion
1. Identify blocking sessions via pg_stat_activity:
   SELECT pid, query, state, age(clock_timestamp(), query_start) FROM pg_stat_activity WHERE state != 'idle' AND wait_event_type = 'Lock';
2. Terminate long-running rogue query causing lock cascades:
   SELECT pg_terminate_backend(PID);
3. If pool is saturated due to connection leak, scale read-replicas and cycle connection poolers (PgBouncer).
4. Restart application worker pools in rolling fashion.

### 4.3 Webhook Ingestion Backlog / Message Queue Lag
1. Check Kafka consumer lag on topic payment-event-ingest.
2. If lag exceeds 50,000 messages, increase consumer partition count and scale Kubernetes deployment replicas:
   kubectl scale deployment/payment-consumer --replicas=20
3. Inspect dead-letter queue (DLQ) for unparseable payload schemas.
4. Route failed payloads to quarantine bucket for replay after hotfix.

## 5. Post-Incident Review (PIR) & Blameless Post-Mortem
Every SEV-1 and SEV-2 requires a formal post-mortem document within 48 hours containing:
1. Executive summary & business impact (lost revenue, affected transactions).
2. Detailed chronological event timeline (all timestamps in UTC and IST).
3. 5-Whys root cause analysis.
4. What went well vs. what went wrong.
5. Actionable preventive measures with assigned Jira ticket IDs and target release dates.
