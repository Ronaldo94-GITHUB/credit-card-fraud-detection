# Career Presentation Kit

## 30-second pitch

Desenvolvi um sistema de detecção de fraudes em cartões de crédito e evoluí o projeto de um classificador XGBoost para uma plataforma completa de Machine Learning em produção. A solução possui FastAPI, PostgreSQL, React, observabilidade, drift com PSI e KS, Model Registry, Champion/Challenger, Ground Truth, retraining governado, Feature Contracts, TreeSHAP, Security Hardening, testes de performance, CI/CD e dashboard executivo com relatório em PDF.

## 2-minute interview pitch

O projeto começou com um problema clássico de classificação altamente desbalanceada para detecção de fraude. Estruturei o pipeline separando treino, validação e teste, tratei o desbalanceamento e usei a validação para selecionar o threshold. O modelo final é um XGBoost avaliado com Precision, Recall, F1, F2, ROC-AUC e Average Precision.

Depois transformei o modelo em uma solução de produção com FastAPI, persistência em PostgreSQL e frontend React/Vite. A partir daí, implementei observabilidade, métricas persistentes, séries temporais, drift estatístico com PSI e KS e alertas MLOps.

Também criei um Model Registry com versionamento, checksums, Champion/Challenger, Continuous Evaluation, promoção controlada e rollback. Para reduzir risco de retreinar com dados pouco confiáveis, implementei Ground Truth de produção e um gate de retraining que pode fazer safe skip quando não há labels suficientes.

A consistência entre treino e serving é protegida por Feature Contracts versionados e fingerprint de schema. Para explicabilidade, integrei TreeSHAP. A API também possui hardening de segurança, rate limiting, auditoria, Request IDs e quality gates de CI/CD. Por fim, criei um dashboard executivo e relatório A4/PDF para apresentar saúde, drift, performance e governança de forma simples.

## Key project metrics

- Precision: 80.52%
- Recall: 83.78%
- F1: 82.12%
- F2: 83.11%
- ROC-AUC: 96.69%
- Average Precision: 83.30%
- Threshold: 0.36
- Test confusion matrix: TN 42633 / FP 15 / FN 12 / TP 62

## Curriculum bullets

- Desenvolvi solução de detecção de fraude com XGBoost, tratamento de desbalanceamento e threshold otimizado em validação.
- Implementei API de inferência com FastAPI, persistência PostgreSQL e frontend React/Vite.
- Estruturei ciclo MLOps com Model Registry, Champion/Challenger, Continuous Evaluation, rollback e promoção controlada.
- Implementei observabilidade, séries temporais, drift estatístico com PSI/KS e alertas operacionais.
- Criei Ground Truth de produção, métricas reais e retraining governado com safe skip quando os dados são insuficientes.
- Implementei Feature Contracts versionados e fingerprint SHA-256 para reduzir risco de training-serving skew.
- Integrei TreeSHAP para explicabilidade de previsões em produção.
- Adicionei Security Hardening, rate limiting, auditoria, testes de performance e pipelines CI/CD com GitHub Actions.
- Criei dashboard executivo e relatório A4/PDF para apresentação de KPIs, drift, performance e governança.

## LinkedIn project description

**Credit Card Fraud Detection | Machine Learning & MLOps**

Desenvolvi uma plataforma de detecção de fraude utilizando Python e XGBoost e evoluí o projeto para uma arquitetura de produção com FastAPI, PostgreSQL e React. A solução inclui observabilidade, drift com PSI/KS, Model Registry, Champion/Challenger, Ground Truth, retraining governado, Feature Contracts, TreeSHAP, segurança, performance, CI/CD e dashboard executivo com relatório PDF.

Tecnologias: Python · XGBoost · scikit-learn · pandas · SHAP · FastAPI · PostgreSQL · React · Vite · Docker · GitHub Actions · Render · MLOps

## Interview questions to rehearse

### Why XGBoost?

É adequado para dados tabulares, oferece bom desempenho em classificação e permite controlar hiperparâmetros, pesos de classe e probabilidades de saída para threshold tuning.

### Why not accuracy?

Fraude é um problema fortemente desbalanceado. Accuracy pode parecer alta mesmo com um modelo ruim. Por isso o projeto acompanha Precision, Recall, F1, F2, ROC-AUC e Average Precision.

### Why F2?

F2 dá mais peso ao Recall. No contexto de fraude, perder uma fraude verdadeira pode ter custo maior do que gerar alguns falsos positivos.

### How did you avoid leakage?

A seleção de threshold foi feita no conjunto de validação e o holdout final foi mantido separado para avaliação final.

### What is PSI?

Population Stability Index mede diferença entre distribuições de referência e produção. O projeto utiliza PSI como um dos sinais de drift.

### What is KS?

A estatística Kolmogorov-Smirnov mede a distância entre distribuições acumuladas e complementa o monitoramento de drift.

### What is Champion/Challenger?

Champion é o modelo ativo. Challenger é uma versão candidata comparada por critérios controlados antes de qualquer promoção.

### How does retraining work?

O retraining exige Ground Truth suficiente e representação mínima das duas classes. Se os requisitos não forem atendidos, o pipeline termina com safe skip.

### Why Feature Contracts?

Eles garantem nomes, ordem, transformações e versão das features entre treino, retraining e inferência, reduzindo training-serving skew.

### How is explainability implemented?

TreeSHAP calcula contribuições locais das features para cada previsão, mostrando fatores que aumentam ou reduzem o risco estimado.

### How is the API protected?

O projeto usa API key administrativa, rate limiting, Request IDs, auditoria, limites de payload, validação de Content-Type, Host header protection, security headers e HSTS em HTTPS.

### How would you scale it?

Separaria serving e workloads MLOps, usaria múltiplas réplicas do backend, store compartilhado para rate limiting, banco gerenciado, observabilidade centralizada e infraestrutura cloud com autoscaling conforme carga real.

## Demo order for interviews

1. Abrir o frontend público e executar uma previsão.
2. Mostrar o Executive MLOps Dashboard.
3. Trocar o período entre 24h, 7d e 30d.
4. Mostrar drift, alertas, Ground Truth e governança.
5. Abrir o Executive Report e demonstrar exportação para PDF.
6. Mostrar rapidamente o diagrama de arquitetura no README.
7. Mostrar Model Registry, Feature Contract e workflows de CI/CD.
8. Encerrar explicando que promoção e retraining permanecem governados.

## Screenshot checklist

Capturar imagens limpas de:

- frontend principal;
- resultado de uma previsão;
- Executive MLOps Dashboard inteiro;
- cards de KPIs;
- gráficos de inferências, latência e fraude prevista;
- seção de governança;
- relatório executivo em modo A4;
- diagrama Mermaid do README;
- GitHub Actions com workflows aprovados.

Evitar qualquer screenshot contendo API keys, URLs secretas, variáveis de ambiente, tokens ou dados sensíveis.

## Target roles

Este projeto é especialmente relevante para:

- Machine Learning Engineer Júnior;
- MLOps Engineer Júnior;
- AI Engineer Júnior com foco em ML;
- Data Scientist Júnior;
- Python Backend Developer Júnior com ML;
- Analista de IA / Machine Learning Júnior.
