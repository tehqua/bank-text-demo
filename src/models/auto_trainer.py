from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime
from pathlib import Path
from src.models.sentiment.classifier import SentimentClassifier
from src.models.topic.auto_topic import AutoTopicModel
from src.models.trainer import train_sentiment_model, train_topic_auto_model
from src.agents.message_bus import MessageBus, Message, MessageType, MessagePriority
from src.utils.logger import default_logger as logger
from config.settings import SENTIMENT_MODEL_DIR, TOPIC_MODEL_DIR

class AutoTrainer:
    def __init__(self, agent_id: str = "AutoTrainer"):
        self.agent_id = agent_id
        self.message_bus = MessageBus()
        self.training_queue: List[Dict[str, Any]] = []
        self.training_history: List[Dict[str, Any]] = []
        self.min_samples_for_training = 10
        self.retrain_threshold_accuracy = 0.7

        self._subscribe_to_events()
        logger.info(f"{self.agent_id} initialized")

    def _subscribe_to_events(self):
        self.message_bus.subscribe("model.degradation_detected", self.handle_degradation)
        self.message_bus.subscribe("data.new_labeled", self.handle_new_labeled_data)
        self.message_bus.subscribe("training.request", self.handle_training_request)

    def handle_degradation(self, message: Message):
        payload = message.payload
        model_id = payload.get('model_id')
        severity = payload.get('severity', 'medium')

        logger.warning(f"Model degradation detected: {model_id}, severity: {severity}")

        self.training_queue.append({
            "model_id": model_id,
            "reason": "performance_degradation",
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "priority": MessagePriority.HIGH if severity == "high" else MessagePriority.MEDIUM
        })

        self.message_bus.publish(Message(
            type=MessageType.EVENT,
            sender=self.agent_id,
            topic="training.queued",
            payload={"model_id": model_id, "reason": "degradation"}
        ))

    def handle_new_labeled_data(self, message: Message):
        payload = message.payload
        data_size = payload.get('data_size', 0)
        model_type = payload.get('model_type', 'unknown')

        logger.info(f"New labeled data received: {data_size} samples for {model_type}")

        if data_size >= self.min_samples_for_training:
            self.training_queue.append({
                "model_type": model_type,
                "reason": "new_data_available",
                "data_size": data_size,
                "timestamp": datetime.now().isoformat(),
                "priority": MessagePriority.MEDIUM
            })

            self.message_bus.publish(Message(
                type=MessageType.EVENT,
                sender=self.agent_id,
                topic="training.queued",
                payload={"model_type": model_type, "reason": "new_data"}
            ))

    def handle_training_request(self, message: Message):
        payload = message.payload
        self.training_queue.append({
            "model_type": payload.get('model_type'),
            "reason": "manual_request",
            "timestamp": datetime.now().isoformat(),
            "priority": MessagePriority.HIGH
        })

    def train_sentiment_auto(self, df: pd.DataFrame, model_name: str = "sentiment_auto") -> Dict[str, Any]:
        if 'comment_lower' not in df.columns or 'sentiment_label' not in df.columns:
            raise ValueError("DataFrame must have 'comment_lower' and 'sentiment_label' columns")

        texts = df['comment_lower'].tolist()
        labels = df['sentiment_label'].tolist()

        if len(texts) < self.min_samples_for_training:
            raise ValueError(f"Need at least {self.min_samples_for_training} samples, got {len(texts)}")

        logger.info(f"Auto-training sentiment model with {len(texts)} samples")

        try:
            model, metrics = train_sentiment_model(texts, labels, model_name, log_mlflow=False)

            self.training_history.append({
                "model_type": "sentiment",
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
                "data_size": len(texts)
            })

            self.message_bus.publish(Message(
                type=MessageType.EVENT,
                sender=self.agent_id,
                topic="model.trained",
                payload={
                    "model_name": model_name,
                    "model_type": "sentiment",
                    "metrics": metrics,
                    "training_data_size": len(texts),
                    "hyperparameters": {"min_samples": self.min_samples_for_training}
                }
            ))

            logger.info(f"Sentiment model trained successfully, accuracy: {metrics.get('accuracy', 0):.3f}")
            return metrics

        except Exception as e:
            logger.error(f"Auto-training failed: {e}")
            self.message_bus.publish(Message(
                type=MessageType.EVENT,
                sender=self.agent_id,
                topic="training.failed",
                payload={"model_type": "sentiment", "error": str(e)},
                priority=MessagePriority.HIGH
            ))
            raise

    def train_topic_auto(self, texts: List[str], n_clusters: int = 5, model_name: str = "topic_auto") -> Dict[str, Any]:
        if len(texts) < self.min_samples_for_training:
            raise ValueError(f"Need at least {self.min_samples_for_training} samples, got {len(texts)}")

        logger.info(f"Auto-training topic model with {len(texts)} samples, {n_clusters} clusters")

        try:
            model = train_topic_auto_model(texts, n_clusters, log_mlflow=False)

            metrics = {
                "n_clusters": n_clusters,
                "n_samples": len(texts),
                "silhouette_score": 0.0
            }

            self.training_history.append({
                "model_type": "topic",
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
                "data_size": len(texts)
            })

            self.message_bus.publish(Message(
                type=MessageType.EVENT,
                sender=self.agent_id,
                topic="model.trained",
                payload={
                    "model_name": model_name,
                    "model_type": "topic",
                    "metrics": metrics,
                    "training_data_size": len(texts),
                    "hyperparameters": {"n_clusters": n_clusters}
                }
            ))

            logger.info(f"Topic model trained successfully with {n_clusters} clusters")
            return metrics

        except Exception as e:
            logger.error(f"Topic auto-training failed: {e}")
            self.message_bus.publish(Message(
                type=MessageType.EVENT,
                sender=self.agent_id,
                topic="training.failed",
                payload={"model_type": "topic", "error": str(e)},
                priority=MessagePriority.HIGH
            ))
            raise

    def process_training_queue(self, df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        if not self.training_queue:
            logger.info("Training queue is empty")
            return []

        results = []

        self.training_queue.sort(key=lambda x: x.get('priority', MessagePriority.MEDIUM).value, reverse=True)

        for task in self.training_queue[:3]:
            try:
                model_type = task.get('model_type')

                if model_type == 'sentiment' and df is not None:
                    metrics = self.train_sentiment_auto(df)
                    results.append({
                        "task": task,
                        "status": "success",
                        "metrics": metrics
                    })

                elif model_type == 'topic' and df is not None:
                    texts = df['comment_lower'].tolist()
                    metrics = self.train_topic_auto(texts)
                    results.append({
                        "task": task,
                        "status": "success",
                        "metrics": metrics
                    })

                else:
                    results.append({
                        "task": task,
                        "status": "skipped",
                        "reason": "insufficient_data"
                    })

            except Exception as e:
                logger.error(f"Training task failed: {e}")
                results.append({
                    "task": task,
                    "status": "failed",
                    "error": str(e)
                })

        self.training_queue = self.training_queue[3:]

        return results

    def get_training_statistics(self) -> Dict[str, Any]:
        return {
            "queue_size": len(self.training_queue),
            "total_trainings": len(self.training_history),
            "recent_trainings": self.training_history[-5:],
            "pending_tasks": self.training_queue
        }

    def clear_queue(self):
        self.training_queue.clear()
        logger.info("Training queue cleared")
