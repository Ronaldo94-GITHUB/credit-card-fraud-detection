# Model Registry Runbook

## Purpose

The model registry separates model lifecycle
management from application source code.

The runtime resolves the active production model
through:

models/model_registry.json

## Initial production version

The current tuned XGBoost production model is
registered as:

v1.0.0

## Model stages

candidate

A registered model that is not currently serving
production traffic.

production

The model version currently selected for inference.

archived

A previously active version retained for rollback.

## Check registry status

Run:

python scripts/model_registry_cli.py status

## Register a new candidate

Example:

python scripts/model_registry_cli.py register \
  --version v1.1.0 \
  --path models/new_model.joblib \
  --name tuned_xgboost_v1_1 \
  --description "Candidate model"

Registration does not automatically make the
candidate active.

## Promote a candidate

Run:

python scripts/model_registry_cli.py promote \
  --version v1.1.0

The registry records:

- new active version
- previous production version
- promotion timestamp
- model checksum
- lifecycle history

## Rollback

Run:

python scripts/model_registry_cli.py rollback

Rollback switches the active version back to the
previous registered production version.

## Integrity verification

Every registered model contains a SHA-256 checksum.

The runtime validates the active model file against
the stored checksum before using the registry model.

If registry validation fails, the existing runtime
fallback remains available.

## Production process

Recommended promotion flow:

1. Train candidate model.
2. Evaluate candidate metrics.
3. Save model artifact.
4. Register candidate.
5. Run tests.
6. Review model registry diff.
7. Promote candidate.
8. Commit registry change.
9. Push through Production CI.
10. Deploy.
11. Run smoke tests.
12. Monitor production.

## Model rollback vs application rollback

Model rollback changes the active model version.

Application rollback restores an earlier deployed
application revision.

They are separate operational controls.

## Registry audit trail

The history field records:

- initial_import
- register
- promote
- rollback

## Safety

Never overwrite an existing model version.

Create a new semantic version for each candidate.

Examples:

v1.0.0
v1.1.0
v1.2.0
v2.0.0
