# Executive MLOps Dashboard

## Purpose

Phase 29 adds an executive layer on top of the existing
production-oriented MLOps architecture.

The goal is to make the system easier to demonstrate to:

- technical leadership;
- recruiters;
- managers;
- product stakeholders;
- engineering teams.

## Routes

### Executive dashboard

`GET /executive`

The dashboard provides an aggregated executive view.

### Executive report

`GET /executive/report?period=7d`

The report is optimized for A4 printing.

Use the **Generate PDF** button and select
**Save as PDF** in the browser print dialog.

## Supported periods

- 24h
- 7d
- 30d

## Executive indicators

The dashboard attempts to summarize existing project
signals from:

- model information;
- persistent metrics;
- temporal metrics;
- statistical drift;
- MLOps alerts;
- Ground Truth metrics;
- health;
- readiness.

The page uses defensive field discovery so unavailable
optional metrics are displayed as `--` rather than
breaking the executive dashboard.

## Sections

The dashboard contains:

1. Executive Summary
2. Active Model
3. Inference Volume
4. Predicted Fraud Rate
5. Latency
6. Statistical Drift
7. MLOps Alerts
8. Model Health
9. Ground Truth
10. Performance
11. Governance
12. Executive Recommendation

## Security

The dashboard does not embed the administrative API key.

It displays aggregated information and does not render
complete individual transaction payloads.

If a metric endpoint requires administrative
authentication, the corresponding executive value may
appear as unavailable or restricted.

## PDF workflow

The executive report uses a print-optimized HTML layout.

Flow:

Dashboard

-> Executive Report

-> Generate PDF

-> Browser print dialog

-> Save as PDF

This keeps PDF generation presentation-friendly without
introducing a server-side PDF dependency.

## Governance

The executive recommendation does not automatically:

- retrain a model;
- promote a challenger;
- rollback a model;
- change production configuration.

Those actions remain controlled by the existing governed
MLOps lifecycle.
