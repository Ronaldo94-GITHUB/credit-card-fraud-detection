# Production Observability Runbook

## Purpose

This runbook documents operational monitoring
for the credit card fraud detection service.

## Production monitor

The production monitor verifies:

- health endpoint
- readiness endpoint
- model information endpoint
- security status endpoint
- persistent metrics endpoint
- endpoint latency
- administrative security controls

## Monitor schedule

GitHub Actions executes the production monitor
twice per hour.

The workflow can also be started manually from
the Actions tab.

## Status levels

### Healthy

All endpoints are available and measured latency
is below the warning threshold.

### Warning

All critical functionality is available, but at
least one monitored endpoint exceeded the warning
latency threshold.

### Critical

A critical status is generated when:

- a monitored endpoint is unavailable
- a monitored endpoint returns an unsuccessful status
- the security controls are not healthy
- endpoint latency reaches the critical threshold
- production readiness cannot be established

## Current latency thresholds

Warning:

2500 ms

Critical:

10000 ms

## Monitoring report

The monitor generates:

reports/runtime/production_monitor.json

In GitHub Actions the report is uploaded as an
artifact.

## Incident response

When Production Monitoring fails:

1. Open GitHub Actions.
2. Open Production Monitoring.
3. Review the failed step.
4. Download the production-monitor-report artifact.
5. Identify the failed endpoint.
6. Check Render logs.
7. Check the /readiness endpoint.
8. Check PostgreSQL availability.
9. Check model loading.
10. Check recent deployment history.

If the incident started immediately after a deploy,
follow the rollback process documented in:

docs/production-runbook.md

## Security alert

The monitor expects the following controls to be
active:

- ADMIN_API_KEY configured
- request IDs enabled
- audit logging enabled

The administrative key value is never read or
stored by this monitoring workflow.

## Manual execution

Run:

python scripts/production_monitor.py

Expected healthy result:

PRODUCTION_STATUS=healthy
FAILED_ENDPOINTS=0
SECURITY_HEALTHY=True
PRODUCTION_ALERT_LEVEL=NONE
PRODUCTION_MONITOR_OK=True

## Operational objective

The production monitor is intended to detect:

- downtime
- readiness failures
- degraded API latency
- lost administrative protection
- disabled audit controls
- production endpoint failures
