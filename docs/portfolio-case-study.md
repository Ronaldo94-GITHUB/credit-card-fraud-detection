# Portfolio Case Study

## Credit Card Fraud Detection — Production MLOps System

### Problem

Credit-card fraud detection is a highly imbalanced binary
classification problem.

A useful solution requires more than training a classifier.
It also requires monitoring, traceability, deployment
safety and controlled model evolution.

### Solution

This project implements a production-oriented fraud
detection platform using:

- Python
- XGBoost
- scikit-learn
- pandas
- SHAP
- FastAPI
- PostgreSQL
- React
- Vite
- Docker
- GitHub Actions
- Render

### Machine Learning

The ML pipeline includes:

- stratified train, validation and test splits
- class imbalance handling
- validation-based threshold optimization
- Precision
- Recall
- F1
- F2
- ROC-AUC
- Average Precision
- Confusion Matrix
- champion/challenger evaluation

### MLOps

The project includes:

- persistent inference telemetry
- statistical drift detection
- PSI and KS monitoring
- temporal monitoring
- MLOps alerts
- model registry
- model versioning
- checksum validation
- rollback
- continuous evaluation
- controlled promotion
- production ground truth
- governed retraining
- versioned feature contracts
- schema fingerprinting
- scheduled monitoring

### Explainable AI

TreeSHAP explains individual model predictions.

Explanations are associated with:

- the active model
- the active feature contract
- the persisted inference event

### Security

The API includes:

- administrative API-key protection
- prediction rate limiting
- request IDs
- audit logging
- request payload limits
- JSON Content-Type validation
- Host header protection
- security response headers
- HSTS for HTTPS
- dependency vulnerability auditing

### Performance Engineering

The project measures:

- model inference latency
- API latency
- concurrent requests
- throughput
- error rate
- p50 latency
- p95 latency
- p99 latency

Performance tests are used as regression gates rather than
claims of guaranteed production capacity.

### Production

Backend API:

https://credit-card-fraud-detection-v5li.onrender.com

Swagger / OpenAPI:

https://credit-card-fraud-detection-v5li.onrender.com/docs

Frontend:

https://credit-card-fraud-detection-frontend-k6ki.onrender.com

### Engineering Decisions

Important safeguards include:

1. Threshold selection uses validation data.

2. The final test holdout remains isolated.

3. Ground truth must be confirmed before retraining.

4. Retraining safely skips when data is insufficient.

5. Evaluation can recommend a model but does not
   automatically promote it.

6. Model promotion supports rollback.

7. Feature schemas are versioned and fingerprinted.

8. Automated load testing targets a local service instead
   of intentionally stressing production.

### What This Project Demonstrates

This repository demonstrates practical experience with:

- Machine Learning
- imbalanced classification
- Python
- FastAPI
- PostgreSQL
- APIs
- MLOps
- model governance
- monitoring
- drift detection
- Explainable AI
- security
- CI/CD
- Docker
- deployment
- performance engineering

### Interview Summary

I started with an XGBoost credit-card fraud classifier and
evolved it into a production-oriented MLOps system.

The project now includes FastAPI serving, PostgreSQL
persistence, monitoring, drift detection, a model registry,
champion/challenger evaluation, controlled promotion,
production ground truth, governed retraining, versioned
feature contracts, TreeSHAP explainability, API security
and performance regression gates.

The application is deployed on Render and its engineering
quality is validated through automated GitHub Actions
workflows.

### Suitable Portfolio Areas

This project can demonstrate skills relevant to junior
positions such as:

- Machine Learning Engineer
- AI Engineer
- MLOps Engineer
- Data Scientist
- Python Backend Developer working with ML systems
