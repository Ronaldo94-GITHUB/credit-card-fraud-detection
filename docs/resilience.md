# Resilience and Safe Failure Handling

The production API includes defensive behavior for
critical dependency failures.

## Covered scenarios

- database unavailable;
- missing model artifact;
- readiness failure;
- model-info failure;
- dependency health degradation.

## Health versus Readiness

`GET /health`

The endpoint reports operational component status.

A database failure can be exposed without requiring the
application process itself to crash.

`GET /readiness`

The endpoint is stricter.

If a critical dependency such as the database or model is
unavailable, readiness returns HTTP 503.

This behavior is important for container orchestration and
production traffic management.

## Safe failure principle

The project distinguishes:

- application process alive;
- service ready to receive production traffic;
- external dependency availability.

This avoids reporting a service as ready when the model or
database required for production operation is unavailable.

## Automated tests

Resilience scenarios are validated through isolated tests
using monkeypatch-based failure simulation.

No real production database or model artifact is intentionally
damaged during these tests.

## Production value

These tests demonstrate that failure scenarios are treated as
part of system design rather than exceptional manual cases.

## Prediction-path resilience

The `/predict` execution path is also validated against
transient and internal failures.

Covered scenarios include:

- inference engine failure;
- model metadata failure;
- inference persistence failure;
- audit persistence failure;
- slow inference;
- recovery after a transient persistence failure;
- protection against leaking internal exception details.

### Failure contract

Unexpected prediction-path failures return:

`HTTP 500`

with the public message:

`Prediction failed.`

Internal exception details remain in server-side logs rather
than being exposed in the HTTP response.

### Recovery behavior

A transient dependency failure in one request does not place
the application in a permanently failed state.

A subsequent valid request can execute normally after the
dependency becomes available again.

### Safety

These tests use mocked failures only.

No production database is disconnected, no production model
is removed, and no production transaction is intentionally
corrupted.
