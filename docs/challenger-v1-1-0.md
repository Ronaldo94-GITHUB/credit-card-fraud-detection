# Challenger v1.1.0 Runbook

## Purpose

Phase 20 introduces the first real challenger
model into the versioned model lifecycle.

Champion:

v1.0.0

Challenger:

v1.1.0

## Challenger training

Run:

python scripts/train_challenger_v1_1_0.py

The candidate uses:

- XGBoost
- deterministic random state
- class imbalance weighting
- validation threshold optimization
- labeled validation metrics
- labeled test metrics

## Safety

The challenger is trained on the training split.

The classification threshold is selected using the
validation split.

The final champion/challenger comparison uses the
test holdout.

The test holdout is not used to fit the candidate.

## Artifact

Candidate artifact:

models/challenger_v1_1_0.joblib

## Training report

Candidate report:

reports/challenger_v1_1_0_metrics.json

## Registration

After successful training the artifact is registered
as:

v1.1.0

stage:

candidate

Registration does not activate the model.

## Continuous evaluation

Run:

python scripts/continuous_model_evaluation.py

The evaluation compares:

v1.0.0 champion

versus

v1.1.0 challenger

using the promotion gate created in Phase 19.

## Promotion

Promotion remains explicit.

A candidate should only be promoted if:

promotion_recommended = true

and its metrics are reviewed.

## Important rule

Phase 20 does not automatically replace the
production model.

The current champion remains active unless a later
promotion command explicitly changes the registry.
