# Capacity and Cost Planning

## Quick end-to-end benchmark

Local FastAPI `/predict` benchmark:

- P50 latency: 62.82 ms
- P95 latency: 70.04 ms
- P99 latency: 70.04 ms
- Measured throughput: 15.74 requests/second
- Sustainable single-worker estimate: 9.99 requests/second
- Estimated monthly capacity: 26,264,541 inferences
- Successful requests: 10/10

The sustainable estimate applies a 70% utilization safety factor.

These values are a local planning baseline and not a production SLA.
Actual production capacity depends on CPU, memory, database latency,
network, concurrency, worker count and infrastructure configuration.
