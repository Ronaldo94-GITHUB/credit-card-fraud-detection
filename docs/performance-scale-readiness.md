# Performance and Scale Readiness

## Phase 27

This phase adds repeatable performance regression testing.

## Model benchmark

Command:

python scripts/benchmark_model_inference.py

Metrics:

- p50
- p95
- p99
- average
- minimum
- maximum

Initial model gate:

p95 <= 1000 ms

## Local HTTP load test

Command:

python scripts/load_test_api.py \
  --base-url http://127.0.0.1:8765 \
  --endpoint /health \
  --requests 120 \
  --concurrency 12

Metrics:

- total requests
- successful requests
- failed requests
- error rate
- throughput
- p50
- p95
- p99

Initial regression gate:

p95 <= 1000 ms

error rate <= 1 percent

throughput >= 5 requests per second

## Safety

Automated load testing targets the local API.

Production Render is not intentionally load tested.

## Important

These measurements are regression baselines.

They do not represent guaranteed production capacity.

Production capacity depends on CPU, RAM, workers,
database connections, networking and infrastructure.
