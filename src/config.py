from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

DATASET_URL = (
    "https://storage.googleapis.com/"
    "download.tensorflow.org/data/creditcard.csv"
)

DATASET_PATH = DATA_DIR / "creditcard.csv"

BEST_MODEL_PATH = MODELS_DIR / "best_model.joblib"
XGBOOST_MODEL_PATH = MODELS_DIR / "xgboost_model.joblib"

TUNED_XGBOOST_MODEL_PATH = (
    MODELS_DIR / "tuned_xgboost_model.joblib"
)

METRICS_PATH = (
    REPORTS_DIR / "model_metrics.csv"
)

METADATA_PATH = (
    REPORTS_DIR / "training_metadata.json"
)

TUNING_RESULTS_PATH = (
    REPORTS_DIR / "xgboost_tuning_results.csv"
)

TUNED_METRICS_PATH = (
    REPORTS_DIR / "tuned_xgboost_metrics.json"
)

TUNED_METADATA_PATH = (
    REPORTS_DIR / "tuned_xgboost_metadata.json"
)

RANDOM_STATE = 42

TEST_SIZE = 0.15
VALIDATION_SIZE = 0.15

TARGET_COLUMN = "Class"
