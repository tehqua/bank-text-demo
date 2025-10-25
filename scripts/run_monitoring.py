import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.etl.loader import load_and_validate
from src.etl.preprocessor import preprocess_dataframe
from src.models.topic.auto_topic import AutoTopicModel
from src.models.sentiment.classifier import SentimentClassifier
from src.agents.goal_manager import GoalManager
from src.agents.monitor import Monitor
from src.agents.planner import Planner
from src.agents.executor import Executor
from src.agents.memory import Memory
from config.settings import TOPIC_MODEL_DIR, SENTIMENT_MODEL_DIR
from src.utils.logger import setup_logger

logger = setup_logger("monitoring", "logs/monitoring.log")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run monitoring and agentic actions")
    parser.add_argument("--data", required=True, help="Path to CSV data")
    parser.add_argument("--execute", action="store_true", help="Execute plan (not dry run)")
    parser.add_argument("--save-baseline", action="store_true", help="Save as new baseline")

    args = parser.parse_args()

    logger.info(f"Starting monitoring job at {datetime.now()}")
    logger.info(f"Loading data from {args.data}")

    df = load_and_validate(args.data)
    df = preprocess_dataframe(df)

    texts = df['comment_lower'].tolist()

    topic_model_path = TOPIC_MODEL_DIR / "topic_auto"
    if topic_model_path.exists():
        topic_model = AutoTopicModel.load(topic_model_path)
        topic_labels, _ = topic_model.predict(texts)
    else:
        logger.warning("No topic model found")
        topic_labels = ["Unknown"] * len(texts)

    sentiment_model_path = SENTIMENT_MODEL_DIR / "sentiment_model"
    if sentiment_model_path.exists():
        sentiment_model = SentimentClassifier.load(sentiment_model_path)
        sentiment_labels, sentiment_scores, _ = sentiment_model.predict_with_scores(texts)
    else:
        logger.warning("No sentiment model found")
        from src.models.sentiment.fallback import fallback_predict
        sentiment_labels, sentiment_scores = fallback_predict(texts)

    df['topic_label'] = topic_labels
    df['sentiment_label'] = sentiment_labels
    df['sentiment_score'] = sentiment_scores

    monitor = Monitor()
    current_metrics = monitor.calculate_current_metrics(df)

    logger.info(f"Current metrics: {current_metrics}")

    anomalies = monitor.detect_anomalies(current_metrics)

    if anomalies:
        logger.warning(f"Detected {len(anomalies)} anomalies")
        for anomaly in anomalies:
            logger.warning(f"  - {anomaly['type']}: {anomaly['message']}")
    else:
        logger.info("No anomalies detected")

    goal_manager = GoalManager()
    violations = goal_manager.check_goal_violations(current_metrics)

    if violations:
        logger.warning(f"Detected {len(violations)} goal violations")
        for v in violations:
            logger.warning(f"  - {v['goal']}: {v['reason']}")
    else:
        logger.info("All KPIs within thresholds")

    if anomalies or violations:
        planner = Planner()
        plan = planner.create_plan(violations, anomalies)
        plan = planner.prioritize_actions(plan)

        logger.info(f"Generated plan with {len(plan['actions'])} actions")
        for action in plan['actions']:
            logger.info(f"  - {action['priority']}: {action['type']}")

        memory = Memory()
        executor = Executor(memory=memory)

        dry_run = not args.execute
        results = executor.execute_plan(plan, dry_run=dry_run)

        logger.info(f"Plan execution {'(DRY RUN)' if dry_run else '(LIVE)'} completed")
        for result in results:
            logger.info(f"  - {result['action']}: {result['message']}")

    if args.save_baseline:
        monitor.save_baseline(current_metrics)
        logger.info("Baseline saved")

    logger.info("Monitoring job completed")

if __name__ == "__main__":
    main()
