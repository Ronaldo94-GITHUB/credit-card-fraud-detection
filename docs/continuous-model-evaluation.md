# Continuous Model Evaluation Runbook

## Purpose

This process continuously compares the current
production model (champion) with registered
candidate models (challengers).

## Ground truth

True model quality metrics require labeled data.

Therefore:

- precision
- recall
- F1
- F2
- ROC-AUC
- Average Precision

are calculated on the deterministic labeled test
holdout.

Production telemetry is treated separately as an
unlabeled operational proxy.

Production proxy metrics are not allowed to promote
a model automatically.

## Champion

The champion is the active version defined in:

models/model_registry.json

## Challengers

Registered models with stage:

candidate

are evaluated against the same labeled test set.

## Promotion gate

A challenger is recommended only when all criteria
pass.

Minimum F2 gain:

0.005

Maximum tolerated recall drop:

0.010

Maximum tolerated Average Precision drop:

0.002

Maximum tolerated precision drop:

0.020

## Important safety rule

The system generates:

promotion_recommended = true

but does not automatically modify production.

This separates automated evaluation from deployment
authority.

## Run evaluation

Run:

python scripts/continuous_model_evaluation.py

## Report

Generated report:

reports/runtime/model_evaluation.json

## Safe promotion

Only an approved version from the latest evaluation
report can be promoted using:

python scripts/promote_evaluated_model.py \
  --version v1.1.0

## Production telemetry windows

The evaluation report attempts to capture production
runtime telemetry for:

- 24h
- 7d
- 30d

These windows provide operational context but do not
represent fraud ground truth.

## GitHub Actions

Continuous Model Evaluation runs daily and can also
be executed manually.

The evaluation report is uploaded as a workflow
artifact.

## Recommended model lifecycle

1. Train new candidate.
2. Save model artifact.
3. Register candidate version.
4. Run Continuous Model Evaluation.
5. Review champion/challenger metrics.
6. Confirm promotion gate.
7. Promote approved candidate.
8. Commit registry change.
9. Run Production CI.
10. Deploy.
11. Run production smoke tests.
12. Monitor drift and operational metrics.
13. Roll back if production behavior degrades.

## Governance

Model evaluation and model deployment are separate
operations.

This protects production against accidental model
promotion.
