# credit-card-fraud-detection

# 💳 Detecção de Fraudes em Cartões de Crédito com XGBoost + SHAP

Este projeto foi desenvolvido em Python utilizando Google Colab e Jupyter Notebook.  
 [Abrir no Google Colab](https://colab.research.google.com/github/Rogerio5/credit-card-fraud-detection/blob/main/Detector_Fraudes_Transacoes.ipynb) 

 ---

![Capa do Projeto](shap-analysis.png.png)

---

## 🏅 Badges

- 📦 Tamanho do repositório / Repository Size:  
  ![GitHub repo size](https://img.shields.io/github/repo-size/Rogerio5/credit-card-fraud-detection)

- 📄 Licença do projeto / Project License:  
  ![GitHub license](https://img.shields.io/github/license/Rogerio5/credit-card-fraud-detection)

- 📊 AUC do modelo / Model AUC:  
  ![AUC](https://img.shields.io/badge/AUC-97%25-brightgreen)

---

## 📋 Índice / Table of Contents

- [Descrição / Description](#descrição--description)
- [Status / Status](#status--status)
- [Funcionalidades / Features](#funcionalidades--features)
- [Tecnologias / Technologies](#tecnologias--technologies)
- [Dataset / Dataset](#dataset)
- [Execução / Run](#execução--run)
- [Resultados e Visualizações / Results--visuals](#resultados-e-visualizações--results--visuals)
- [Desenvolvedor / Developer](#desenvolvedor--developer)
- [Licença / License](#licença--license)
- [Conclusão / Conclusion](#conclusão--conclusion)

---

## 📖 Descrição / Description

**PT:** Este projeto foca em um dos maiores desafios de Machine Learning no setor financeiro: **Problemas de Classificação Desbalanceada**. O modelo identifica transações fraudulentas em cartões de crédito utilizando **XGBoost**.  
Inclui:
- **Técnicas de Reamostragem (SMOTE)** para lidar com o desbalanceamento.
- **Ajuste de Hiperparâmetros (GridSearchCV)** para otimização de métricas focadas em Recall.
- **SHAP (Shapley Additive exPlanations)** para interpretar e explicar as previsões do modelo.

**EN:** This project focuses on one of the biggest Machine Learning challenges in the financial sector: **Imbalanced Classification Problems**. The model identifies fraudulent credit card transactions using **XGBoost**.  
Includes:
- **Resampling Techniques (SMOTE)** to handle data imbalance.
- **Hyperparameter Tuning (GridSearchCV)** to optimize Recall-focused metrics.
- **SHAP (Shapley Additive exPlanations)** to interpret and explain the model's predictions.

---

## 🚧 Status / Status

✅ **Concluído e pronto para uso** / **Completed and ready to use**

---

## ⚙️ Funcionalidades / Features

| 🧩 Funcionalidade (PT)                  | 💡 Description (EN)                                |
|-----------------------------------------|----------------------------------------------------|
| ⚖️ Tratamento de Dados Desbalanceados | ⚖️ Handling Imbalanced Data (Undersampling/SMOTE) |
| 📈 Análise de Curvas ROC e P-R          | 📈 ROC and Precision-Recall Curve Analysis        |
| 🚀 Modelagem Avançada com XGBoost       | 🚀 Advanced Modeling with XGBoost                 |
| 🎯 Otimização com GridSearchCV          | 🎯 Hyperparameter Optimization via GridSearchCV   |
| 🔥 Explicabilidade com SHAP             | 🔥 Model Explainability using SHAP values         |
| 📊 Métricas de Avaliação Focadas        | 📊 Focused Evaluation Metrics (Recall, F1-Score)  |

---

## 📥 Dataset

O dataset utilizado contém transações de cartões de crédito (`creditcard.csv`).  
Trata-se de um conjunto de dados altamente desbalanceado, onde as fraudes representam uma fração minúscula do total de transações. Ele geralmente pode ser encontrado em plataformas como o Kaggle.

---

## ▶️ Execução / Run

```bash
# Clone o repositório
git clone [https://github.com/Rogerio5/credit-card-fraud-detection.git](https://github.com/Rogerio5/credit-card-fraud-detection.git)

# Acesse a pasta do projeto
cd credit-card-fraud-detection

# Instale as dependências necessárias
pip install -r requirements.txt

# Execute o notebook no Jupyter
jupyter notebook Detector_Fraudes_Transacoes.ipynb
```

---

## 🧰 Tecnologias / Technologies

Python 3.10+

Pandas & NumPy

Scikit-Learn

Imbalanced-Learn (SMOTE)

XGBoost

SHAP

Matplotlib & Seaborn

---

## 👨‍💻 Desenvolvedores

- [Rogerio](https://github.com/Rogerio5)
- [Rogerio](https://github.com/Ronaldo94-GITHUB)
---

## 📜 Licença / License

Este projeto está sob licença MIT. Para mais detalhes, veja o arquivo LICENSE.

This project is under the MIT license. For more details, see the LICENSE file.

---

## 🏁 Conclusão / Conclusion

Um projeto de Ciência de Dados robusto que demonstra não apenas a capacidade de criar modelos preditivos de alta precisão em cenários adversos (dados desbalanceados), mas também a importância da explicabilidade no setor financeiro, garantindo que as decisões do algoritmo sejam transparentes e justificáveis.
