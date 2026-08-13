# Controlled Model Promotion Runbook

## Purpose

Phase 21 connects the Champion/Challenger
evaluation gate to a controlled model promotion.

Target candidate:

v1.1.0

## Promotion rule

Promotion is permitted only when the latest
continuous evaluation report contains:

promotion_recommended = true

for v1.1.0.

If the gate is false, the existing champion remains
active.

## Controlled execution

Run:

python scripts/controlled_model_promotion.py

Possible results:

PROMOTION_ACTION=promoted

The approved challenger became the active model.

PROMOTION_ACTION=retained_champion

The challenger did not pass the evaluation gate and
the current champion was preserved.

PROMOTION_ACTION=already_promoted

The target version was already active.

## Safety

Evaluation does not directly deploy a model.

The explicit controlled promotion command performs
the registry change.

## Promotion decision record

The decision is stored in:

reports/model_promotion_decision_v1_1_0.json

It records:

- promotion recommendation
- promotion action
- active version before
- active version after
- previous version
- promotion gate metrics

## Rollback validation

Run:

python scripts/validate_model_rollback.py

Rollback validation operates on a temporary copy of
the registry.

It does not modify the production registry.

## Real rollback

If the promoted model must be reverted:

python scripts/model_registry_cli.py rollback

Then run:

python scripts/production_smoke_test.py

and:

python scripts/production_monitor.py

## Deployment sequence

1. Evaluate champion and challenger.
2. Review promotion gate.
3. Run controlled promotion.
4. Run regression tests.
5. Validate active model runtime.
6. Validate rollback capability.
7. Commit registry decision.
8. Push through Production CI.
9. Render deploys the new revision.
10. Run production smoke test.
11. Monitor production.
