# Production Retraining Runbook

## Purpose

Phase 23 introduces a governed retraining pipeline
using confirmed production ground truth.

## Data sources

The pipeline uses:

1. Existing original training split.
2. Confirmed production ground truth.

Production labels are added only to the training
portion.

The original validation and test holdouts remain
separate.

## Eligibility gate

Retraining requires at least:

100 labeled production observations

20 positive fraud labels

20 negative legitimate labels

If the minimum requirements are not met, retraining
is skipped safely.

Expected result:

RETRAINING_SKIPPED=True

This is not a pipeline failure.

## Candidate version

The first retrained candidate is:

v1.2.0

## Model lifecycle

Eligible data
→ train v1.2.0
→ validation threshold selection
→ holdout evaluation
→ save artifact
→ register candidate
→ champion/challenger evaluation

## No automatic production promotion

Retraining does not change the active production
model.

automatic_promotion = false

A retrained candidate must still pass evaluation
and controlled promotion.

## Ground truth quality

Only confirmed labels should be used.

Examples:

chargeback
fraud_team
manual_review
bank_confirmation

## Retraining report

Generated at:

reports/runtime/retraining_v1_2_0.json

## Manual execution

Run:

python scripts/run_retraining_pipeline.py

## Scheduled execution

GitHub Actions checks retraining eligibility weekly.

The database connection must be supplied through
the DATABASE_URL GitHub Actions secret.

## Safety

Do not use test holdout observations as retraining
examples.

Do not automatically promote a newly trained model.

Do not create synthetic ground truth simply to
satisfy retraining thresholds.
