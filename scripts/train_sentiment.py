import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.trainer import train_sentiment_model
from src.utils.logger import setup_logger

logger = setup_logger("train_sentiment", "logs/train_sentiment.log")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Train sentiment classifier")
    parser.add_argument("--data", required=True, help="Path to labeled CSV (comment, sentiment_label)")
    parser.add_argument("--model-name", default="sentiment_model", help="Model name")
    parser.add_argument("--mlflow", action="store_true", help="Log to MLflow")

    args = parser.parse_args()

    logger.info(f"Loading training data from {args.data}")
    df = pd.read_csv(args.data)

    if 'comment' not in df.columns or 'sentiment_label' not in df.columns:
        logger.error("CSV must have 'comment' and 'sentiment_label' columns")
        sys.exit(1)

    texts = df['comment'].fillna("").tolist()
    labels = df['sentiment_label'].tolist()

    logger.info(f"Training with {len(texts)} samples")

    model, metrics = train_sentiment_model(texts, labels, model_name=args.model_name, log_mlflow=args.mlflow)

    logger.info(f"Training complete!")
    logger.info(f"Accuracy: {metrics.get('accuracy', 0):.3f}")
    logger.info(f"F1 (macro): {metrics.get('f1_macro', 0):.3f}")
    logger.info(f"F1 (weighted): {metrics.get('f1_weighted', 0):.3f}")

if __name__ == "__main__":
    main()
