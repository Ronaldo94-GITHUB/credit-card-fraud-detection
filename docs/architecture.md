# Production Architecture

## Credit Card Fraud Detection

This repository evolved from a machine-learning fraud
classification project into a production-oriented MLOps
system.

## High-level architecture

```mermaid
flowchart LR
    U[Client / React Frontend]

    API[FastAPI API]

    SEC[Security Middleware]

    FC[Feature Contract]

    MODEL[XGBoost Model]

    DB[(PostgreSQL / SQLite)]

    OBS[Observability]

    GT[Ground Truth]

    EXP[TreeSHAP Explainability]

    REG[Model Registry]

    CE[Continuous Evaluation]

    RT[Governed Retraining]

    CI[GitHub Actions]

    RENDER[Render Production]

    U --> API

    API --> SEC

    SEC --> FC

    FC --> MODEL

    MODEL --> DB

    API --> OBS

    DB --> GT

    GT --> RT

    MODEL --> EXP

    REG --> MODEL

    MODEL --> CE

    CE --> REG

    RT --> REG

    CI --> RENDER

    CI --> CE

    CI --> RT

    CI --> OBS
