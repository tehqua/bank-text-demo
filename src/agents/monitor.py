from datetime import datetime
import json
from pathlib import Path
from src.utils.metrics import detect_drift, detect_negative_spike
from src.agents.message_bus import MessageBus, Message, MessageType, MessagePriority
from src.utils.logger import default_logger as logger

class Monitor:
    def __init__(self, baseline_path=None, agent_id="Monitor"):
        self.agent_id = agent_id
        self.message_bus = MessageBus()
        self.baseline_path = baseline_path or Path("data/baseline_metrics.json")
        self.baseline = self._load_baseline()
        self._subscribe_to_events()
        logger.info(f"{self.agent_id} initialized with message bus")

    def _subscribe_to_events(self):
        self.message_bus.subscribe("monitor.check_anomalies", self.handle_check_anomalies)
        self.message_bus.subscribe("monitor.save_baseline", self.handle_save_baseline)

    def _load_baseline(self):
        if self.baseline_path.exists():
            with open(self.baseline_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_baseline(self, metrics):
        self.baseline_path.parent.mkdir(parents=True, exist_ok=True)
        self.baseline = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        with open(self.baseline_path, 'w', encoding='utf-8') as f:
            json.dump(self.baseline, f, indent=2, ensure_ascii=False)
        logger.info(f"Baseline saved to {self.baseline_path}")

    def detect_anomalies(self, current_metrics):
        anomalies = []

        if not self.baseline or "metrics" not in self.baseline:
            logger.warning("No baseline found, skipping anomaly detection")
            return anomalies

        baseline_metrics = self.baseline["metrics"]

        if "sentiment_distribution" in baseline_metrics and "sentiment_distribution" in current_metrics:
            is_drift, drift_score = detect_drift(
                baseline_metrics["sentiment_distribution"],
                current_metrics["sentiment_distribution"]
            )
            if is_drift:
                anomalies.append({
                    "type": "sentiment_drift",
                    "score": drift_score,
                    "message": f"Sentiment distribution drift detected: {drift_score:.3f}"
                })

        if "topic_distribution" in baseline_metrics and "topic_distribution" in current_metrics:
            is_drift, drift_score = detect_drift(
                baseline_metrics["topic_distribution"],
                current_metrics["topic_distribution"]
            )
            if is_drift:
                anomalies.append({
                    "type": "topic_drift",
                    "score": drift_score,
                    "message": f"Topic distribution drift detected: {drift_score:.3f}"
                })

        baseline_neg_ratio = baseline_metrics.get("negative_ratio", 0)
        current_neg_ratio = current_metrics.get("negative_ratio", 0)
        is_spike, delta = detect_negative_spike(current_neg_ratio, baseline_neg_ratio)

        if is_spike:
            anomalies.append({
                "type": "negative_spike",
                "delta": delta,
                "message": f"Negative sentiment spike: +{delta:.1%}"
            })

        return anomalies

    def calculate_current_metrics(self, df_pandas):
        metrics = {}

        if 'sentiment_label' in df_pandas.columns:
            sentiment_dist = df_pandas['sentiment_label'].value_counts().to_dict()
            metrics["sentiment_distribution"] = sentiment_dist

            total = len(df_pandas)
            negative_count = df_pandas[df_pandas['sentiment_label'].isin(['Negative', 'Very Negative'])].shape[0]
            metrics["negative_ratio"] = negative_count / total if total > 0 else 0

        if 'topic_label' in df_pandas.columns:
            topic_dist = df_pandas['topic_label'].value_counts().to_dict()
            metrics["topic_distribution"] = topic_dist

        metrics["total_count"] = len(df_pandas)
        metrics["timestamp"] = datetime.now().isoformat()

        return metrics

    def handle_check_anomalies(self, message: Message):
        current_metrics = message.payload.get('current_metrics', {})
        anomalies = self.detect_anomalies(current_metrics)
        self.message_bus.respond(message, {"anomalies": anomalies})

        if anomalies:
            self.message_bus.publish(Message(
                type=MessageType.EVENT,
                sender=self.agent_id,
                topic="monitor.anomalies_detected",
                payload={"anomalies": anomalies, "count": len(anomalies)},
                priority=MessagePriority.HIGH
            ))

    def handle_save_baseline(self, message: Message):
        metrics = message.payload.get('metrics', {})
        self.save_baseline(metrics)
        self.message_bus.respond(message, {"status": "success"})

    def store_baseline(self, metrics):
        self.save_baseline(metrics)
        self.message_bus.publish(Message(
            type=MessageType.EVENT,
            sender=self.agent_id,
            topic="monitor.baseline_updated",
            payload={"timestamp": datetime.now().isoformat()}
        ))
