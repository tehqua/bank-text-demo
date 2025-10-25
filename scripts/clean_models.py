import sys
from pathlib import Path
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import TOPIC_MODEL_DIR, SENTIMENT_MODEL_DIR
from src.utils.logger import setup_logger

logger = setup_logger("clean_models", "logs/clean_models.log")

def clean_topic_models():
    topic_auto_path = TOPIC_MODEL_DIR / "topic_auto"
    topic_supervised_path = TOPIC_MODEL_DIR / "topic_supervised"

    for path in [topic_auto_path, topic_supervised_path]:
        if path.exists():
            shutil.rmtree(path)
            logger.info(f"Removed topic model: {path}")
        else:
            logger.info(f"Topic model not found: {path}")

def clean_sentiment_models():
    sentiment_path = SENTIMENT_MODEL_DIR / "sentiment_model"

    if sentiment_path.exists():
        shutil.rmtree(sentiment_path)
        logger.info(f"Removed sentiment model: {sentiment_path}")
    else:
        logger.info(f"Sentiment model not found: {sentiment_path}")

def clean_all_models():
    logger.info("Cleaning all models...")
    clean_topic_models()
    clean_sentiment_models()
    logger.info("All models cleaned!")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clean trained models")
    parser.add_argument("--type", choices=["topic", "sentiment", "all"], default="all",
                       help="Type of models to clean")

    args = parser.parse_args()

    if args.type == "topic":
        clean_topic_models()
    elif args.type == "sentiment":
        clean_sentiment_models()
    else:
        clean_all_models()

    print("Models cleaned successfully!")
