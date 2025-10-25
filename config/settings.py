import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
LABELED_DIR = DATA_DIR / "labeled"
MODEL_DIR = Path(os.getenv("MODEL_DIR", str(DATA_DIR / "model_artifacts")))

TOPIC_MODEL_DIR = MODEL_DIR / "topic"
SENTIMENT_MODEL_DIR = MODEL_DIR / "sentiment"

for d in [RAW_DIR, PROCESSED_DIR, LABELED_DIR, TOPIC_MODEL_DIR, SENTIMENT_MODEL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "file:///./mlruns")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

JIRA_URL = os.getenv("JIRA_URL", "")
JIRA_USER = os.getenv("JIRA_USER", "")
JIRA_TOKEN = os.getenv("JIRA_TOKEN", "")
JIRA_PROJECT = os.getenv("JIRA_PROJECT", "OPS")

KPI_SENTIMENT_ACCURACY_MIN = float(os.getenv("KPI_SENTIMENT_ACCURACY_MIN", "0.88"))
KPI_NEGATIVE_SPIKE_THRESHOLD = float(os.getenv("KPI_NEGATIVE_SPIKE_THRESHOLD", "0.2"))
KPI_DRIFT_THRESHOLD = float(os.getenv("KPI_DRIFT_THRESHOLD", "0.15"))

REQUIRED_COLUMNS = ["comment"]
OPTIONAL_COLUMNS = ["id", "timestamp", "source"]
SENTIMENT_LABELS = ["Very Negative", "Negative", "Neutral", "Positive", "Very Positive", "Mixed"]
