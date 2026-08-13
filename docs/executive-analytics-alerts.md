# Executive Analytics and External Alerts

## Phase 30

Phase 30 extends the executive MLOps layer with:

- operational trend charts;
- print-ready charts in the executive report;
- external alert delivery;
- Slack-compatible webhook payloads;
- scheduled GitHub Actions alert checks.

## Executive charts

The executive dashboard and printable report now contain
three operational trend charts:

1. inference volume;
2. latency;
3. predicted fraud rate.

The charts consume the existing temporal metrics endpoint:

`GET /metrics/timeseries?period=7d`

If temporal data is insufficient, the chart renders a safe
"insufficient data" state instead of failing.

## PDF

The charts use SVG so they remain sharp when the executive
report is printed or saved as PDF.

Flow:

`/executive`

-> `/executive/report?period=7d`

-> Generate PDF

-> Save as PDF

## External alerts

The project supports generic JSON webhooks and
Slack-compatible incoming webhooks.

Configuration:

`MLOPS_ALERT_WEBHOOK_ENABLED=true`

`MLOPS_ALERT_WEBHOOK_URL=<secret webhook url>`

Optional:

`MLOPS_ALERT_WEBHOOK_BEARER_TOKEN=<secret token>`

No webhook secret is stored in the repository.

## Alert policy

External notification occurs only when the MLOps alert
payload indicates:

- warning; or
- critical.

Stable periods do not generate an external notification.

## Scheduled workflow

`.github/workflows/external-mlops-alerts.yml`

The workflow runs twice per hour and can also be executed
manually.

Without configured GitHub secrets the workflow remains
safe and does not send external messages.
