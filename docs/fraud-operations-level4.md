# Fraud Operations Level 4

Senior hardening layer for the fraud
operations platform.

## Capabilities

- Atomic adjudication of case status
  and Ground Truth.
- Immutable case audit history.
- Versioned fraud policy.
- Risk-based operational SLA.
- Deterministic case priority score.
- Case ownership through assignee.
- Small-sample guard for metrics.
- Operational queue KPIs.
- Confirmed fraud exposure.

## Policy

Current version:

`fraud-ops-v2.0.0`

SLA:

- critical: 15 minutes
- high: 60 minutes
- medium: 240 minutes
- low: 1440 minutes

Production metrics remain marked as
`provisional_small_sample` until the
dataset has at least:

- 100 labels
- 20 positive labels
- 20 negative labels

These values intentionally match the
existing governed retraining gate.

## Atomic adjudication

`confirmed_fraud` maps to label `1`.

`false_positive` maps to label `0`.

Case review, Ground Truth and the audit
entry are written in the same database
transaction.

## Endpoints

Public:

- `GET /fraud-operations/policy`

Admin:

- `GET /fraud-operations/operations-kpis`
- `GET /fraud-operations/operational-cases`
- `POST /fraud-operations/cases/{id}/adjudicate`
- `GET /fraud-operations/cases/{id}/history`

## Audit trail

Each adjudication records:

- previous status
- new status
- assignee
- actor
- Ground Truth
- policy version
- model metadata
- probability
- amount
- timestamp
