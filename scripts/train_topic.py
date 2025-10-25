import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.trainer import train_topic_supervised_model, train_topic_auto_model
from src.utils.logger import setup_logger

logger = setup_logger("train_topic", "logs/train_topic.log")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Train topic model")
    parser.add_argument("--data", required=True, help="Path to CSV")
    parser.add_argument("--mode", choices=["auto", "supervised"], default="auto", help="Training mode")
    parser.add_argument("--model-name", help="Model name")
    parser.add_argument("--n-clusters", type=int, default=8, help="Number of clusters for auto mode")
    parser.add_argument("--mlflow", action="store_true", help="Log to MLflow")

    args = parser.parse_args()

    logger.info(f"Loading data from {args.data}")
    df = pd.read_csv(args.data)

    if 'comment' not in df.columns:
        logger.error("CSV must have 'comment' column")
        sys.exit(1)

    texts = df['comment'].fillna("").tolist()

    if args.mode == "auto":
        model_name = args.model_name or "topic_auto"
        logger.info(f"Training auto topic model with {args.n_clusters} clusters")
        model = train_topic_auto_model(texts, n_clusters=args.n_clusters, model_name=model_name, log_mlflow=args.mlflow)
        logger.info("Auto topic model training complete")

    else:
        if 'topic_label' not in df.columns:
            logger.error("For supervised mode, CSV must have 'topic_label' column")
            sys.exit(1)

        labels = df['topic_label'].tolist()
        model_name = args.model_name or "topic_supervised"
        logger.info(f"Training supervised topic model with {len(texts)} samples")
        model, metrics = train_topic_supervised_model(texts, labels, model_name=model_name, log_mlflow=args.mlflow)

        logger.info(f"Supervised topic model training complete")
        logger.info(f"Accuracy: {metrics.get('accuracy', 0):.3f}")
        logger.info(f"F1 (macro): {metrics.get('f1_macro', 0):.3f}")

if __name__ == "__main__":
    main()
