# Production Explainability

## Phase 25

Production model decisions can be explained using
TreeSHAP.

## Endpoint

GET:

/explainability/{inference_event_id}

Query parameter:

top_k

Default:

10

Maximum:

20

## Security

Explainability endpoints require the administrative API key.

Header:

X-Admin-API-Key

The endpoint is not intended as a public prediction API.

## Stored inference linkage

Explanations are produced from the feature payload that was
stored with the original inference event.

This provides traceability between:

prediction

stored event

model

feature contract

SHAP explanation

## Response

The response includes:

inference event ID

model version

feature contract version

schema fingerprint

fraud probability

prediction

threshold

top SHAP factors

direction of each factor

## Direction

Positive SHAP contribution:

increases_fraud_risk

Negative SHAP contribution:

decreases_fraud_risk

Zero contribution:

neutral

## Output space

TreeSHAP values are identified as:

model_raw

They must not be interpreted directly as percentage-point
changes in fraud probability.

## Data minimization

The API does not return the complete raw transaction.

Only the top factors needed for the explanation are returned.

## Governance

Explainability access is administrative and auditable.

Successful explanation requests generate:

event_type=model_explanation

## Validation

Run:

python scripts/validate_production_explainability.py

Expected:

EXPLAINABILITY_READY=True

EXPLANATION_METHOD=TreeSHAP

RAW_TRANSACTION_EXPOSED=False

EXPLAINABILITY_VALIDATION_OK=True

## Feature contract

Explainability uses the active feature contract from:

models/feature_registry.json

This protects feature ordering and prevents silent
training-serving mismatches.

## Important limitation

SHAP explains how the model produced a score.

It does not prove that a transaction is actually fraudulent,
nor does it establish causality.
