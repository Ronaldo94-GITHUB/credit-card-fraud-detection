# End-to-End MLOps Lifecycle

## Overview

The fraud detection system implements an end-to-end model
lifecycle rather than only training and serving a model.

## 1. Data and preprocessing

The project uses a controlled stratified train,
validation and test split.

Feature engineering includes:

- Amount_log
- Time_hours

## 2. Model training

The primary model family is XGBoost.

Class imbalance is handled using class weighting.

Threshold optimization is performed on validation data.

The final test holdout remains separate.

## 3. Model evaluation

Evaluation includes:

- Precision
- Recall
- F1
- F2
- ROC-AUC
- Average Precision
- Confusion Matrix

## 4. Model registry

Model artifacts are versioned in a registry.

The registry supports:

- registration
- active model resolution
- candidate models
- controlled promotion
- rollback
- checksum validation
- model history

Automatic production promotion is disabled.

## 5. Production inference

FastAPI exposes the prediction service.

Inference events are persisted for monitoring,
traceability and later ground-truth linkage.

## 6. Observability

The system records:

- inference counts
- prediction rates
- request latency
- persistent metrics
- temporal metrics

## 7. Drift monitoring

Drift capabilities include:

- statistical drift
- PSI
- two-sample KS
- multiple monitoring periods
- stable, warning and critical statuses

## 8. MLOps alerts

Operational alerts combine signals such as:

- latency
- suspicious prediction rate
- drift status

## 9. Production ground truth

Confirmed labels can be linked to persisted inference
events.

Ground-truth operations are administratively protected
and audited.

## 10. Production metrics

When confirmed labels exist, the system can calculate:

- Precision
- Recall
- F1
- F2
- Confusion Matrix

for production-labeled observations.

## 11. Governed retraining

Retraining requires sufficient confirmed production
ground truth.

The initial eligibility gate requires:

- at least 100 confirmed labels
- at least 20 fraud labels
- at least 20 legitimate labels

When data is insufficient, retraining is skipped safely.

## 12. Continuous evaluation

Champion and challenger models can be compared using
controlled evaluation criteria.

Evaluation may recommend promotion.

It does not automatically modify production.

## 13. Controlled promotion

Production model changes remain governed.

Rollback capability is preserved.

## 14. Feature contracts

Training, retraining and inference share a versioned
feature contract.

The contract protects:

- feature names
- feature count
- feature order
- transformations
- model compatibility

A SHA-256 fingerprint identifies the schema.

## 15. Explainability

TreeSHAP provides local model explanations.

Explanations are linked to:

- model version
- feature contract
- persisted inference event

## 16. Security

The API uses defense-in-depth controls including:

- administrative API key
- rate limiting
- request IDs
- audit logging
- payload limits
- Content-Type validation
- Host header protection
- security headers
- HSTS for HTTPS

## 17. Performance

Performance regression testing measures:

- inference latency
- HTTP latency
- throughput
- error rate
- concurrency
- p50
- p95
- p99

Load testing intentionally targets a local API instance.

## 18. CI/CD

GitHub Actions automates quality, security,
performance and MLOps governance checks.

Production deployment is hosted on Render.

## Core principle

No single metric or automated check is treated as enough
evidence for production promotion.

The lifecycle combines:

- model quality
- operational health
- ground truth
- feature compatibility
- security
- explainability
- performance
- controlled governance
