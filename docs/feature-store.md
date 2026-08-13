# Feature Store and Feature Contract

## Phase 24

The project uses a versioned feature contract to protect
training, retraining and inference compatibility.

Active feature version:

features-v1.0.0

## Raw features

The raw fraud transaction schema contains 30 fields:

Time

V1 through V28

Amount

## Engineered features

Amount_log

Transformation:

log1p(Amount)

Time_hours

Transformation:

Time / 3600

## Feature registry

Registry file:

models/feature_registry.json

The registry stores:

active feature version

raw feature order

engineered features

model feature order

transform definitions

compatible model versions

schema fingerprint

## Schema fingerprint

Each feature contract receives a SHA-256 fingerprint.

A modification to the feature schema changes the fingerprint.

This helps detect silent feature drift and accidental
training-serving skew.

## Training-serving consistency

The same feature contract is shared by:

production inference validation

retraining dataset construction

model compatibility validation

CI feature contract validation

## Breaking changes

Removing a feature

renaming a feature

changing feature meaning

changing feature order required by a model

changing an existing transformation

must create a new feature contract version.

Example:

features-v2.0.0

## Non-breaking evolution

Documentation changes and metadata additions may remain
within the same feature contract when they do not alter
model inputs.

## Model compatibility

Before deployment, the active model bundle is checked
against the active feature contract.

The following must match exactly:

feature names

feature count

feature order

## Validation

Run:

python scripts/validate_feature_contract.py

Expected:

MODEL_FEATURE_COMPATIBLE=True

SYNTHETIC_TRANSFORM_OK=True

FEATURE_CONTRACT_OK=True

## Retraining integration

The Phase 23 retraining pipeline reads its required raw
features from the same central contract.

This prevents separate definitions of training and
production features.

## Governance

Feature schema changes must be reviewed before promotion
of a model that depends on the new contract.

Model promotion and feature contract activation remain
separate governed operations.
