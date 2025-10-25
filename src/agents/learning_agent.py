from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.agents.message_bus import MessageBus, Message, MessageType, MessagePriority
from src.models.active_learner import ActiveLearner
from src.models.auto_trainer import AutoTrainer
from src.utils.logger import default_logger as logger

class ContinuousLearningAgent:
    def __init__(self, agent_id: str = "LearningAgent"):
        self.agent_id = agent_id
        self.message_bus = MessageBus()
        self.active_learner = ActiveLearner(uncertainty_threshold=0.3)
        self.auto_trainer = AutoTrainer()

        self.learning_cycle_interval = timedelta(hours=24)
        self.last_learning_cycle = datetime.now()
        self.performance_baseline: Dict[str, float] = {}
        self.improvement_log: List[Dict[str, Any]] = []

        self._subscribe_to_events()
        logger.info(f"{self.agent_id} initialized")

    def _subscribe_to_events(self):
        self.message_bus.subscribe("data.analyzed", self.handle_analyzed_data)
        self.message_bus.subscribe("model.degradation_detected", self.handle_degradation)
        self.message_bus.subscribe("learning.trigger_cycle", self.handle_trigger_cycle)

    def handle_analyzed_data(self, message: Message):
        payload = message.payload
        df = payload.get('dataframe')
        predictions = payload.get('predictions')
        probabilities = payload.get('probabilities')

        if df is not None and predictions is not None and probabilities is not None:
            self._identify_learning_opportunities(df, predictions, probabilities)

    def handle_degradation(self, message: Message):
        logger.warning(f"Performance degradation detected, initiating learning cycle")
        self.message_bus.publish(Message(
            type=MessageType.EVENT,
            sender=self.agent_id,
            topic="learning.cycle_started",
            payload={"trigger": "degradation"},
            priority=MessagePriority.HIGH
        ))

    def handle_trigger_cycle(self, message: Message):
        logger.info("Learning cycle triggered manually")
        self.last_learning_cycle = datetime.now()

    def _identify_learning_opportunities(self, df: pd.DataFrame, predictions: List[str],
                                        probabilities: np.ndarray):
        texts = df['comment_lower'].tolist() if 'comment_lower' in df.columns else []

        if len(texts) == 0:
            return

        uncertain_samples = self.active_learner.identify_uncertain_samples(
            texts, predictions, probabilities, top_k=20
        )

        if len(uncertain_samples) > 5:
            self.message_bus.publish(Message(
                type=MessageType.EVENT,
                sender=self.agent_id,
                topic="learning.uncertain_samples_found",
                payload={
                    "count": len(uncertain_samples),
                    "avg_uncertainty": float(np.mean([s.uncertainty_score for s in uncertain_samples])),
                    "samples": self.active_learner.get_samples_for_labeling()
                }
            ))

            logger.info(f"Identified {len(uncertain_samples)} uncertain samples for labeling")

    def check_and_trigger_learning_cycle(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        time_since_last = datetime.now() - self.last_learning_cycle

        if time_since_last < self.learning_cycle_interval:
            return {
                "status": "skipped",
                "reason": "too_soon",
                "next_cycle_in": str(self.learning_cycle_interval - time_since_last)
            }

        logger.info("Starting continuous learning cycle")
        self.last_learning_cycle = datetime.now()

        cycle_results = {
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }

        training_stats = self.auto_trainer.get_training_statistics()
        if training_stats['queue_size'] > 0 and df is not None:
            logger.info(f"Processing {training_stats['queue_size']} training tasks")

            training_results = self.auto_trainer.process_training_queue(df)
            cycle_results['actions'].append({
                "action": "auto_training",
                "results": training_results
            })

        active_learning_stats = self.active_learner.get_statistics()
        if active_learning_stats['total_uncertain'] > 0:
            cycle_results['actions'].append({
                "action": "active_learning",
                "uncertain_samples": active_learning_stats
            })

        self.message_bus.publish(Message(
            type=MessageType.EVENT,
            sender=self.agent_id,
            topic="learning.cycle_completed",
            payload=cycle_results,
            priority=MessagePriority.MEDIUM
        ))

        logger.info("Learning cycle completed")
        return cycle_results

    def update_performance_baseline(self, model_type: str, metrics: Dict[str, float]):
        key = f"{model_type}_accuracy"
        old_baseline = self.performance_baseline.get(key, 0.0)
        new_baseline = metrics.get('accuracy', 0.0)

        self.performance_baseline[key] = new_baseline

        improvement = new_baseline - old_baseline
        if abs(improvement) > 0.01:
            self.improvement_log.append({
                "model_type": model_type,
                "timestamp": datetime.now().isoformat(),
                "old_accuracy": old_baseline,
                "new_accuracy": new_baseline,
                "improvement": improvement
            })

            self.message_bus.publish(Message(
                type=MessageType.EVENT,
                sender=self.agent_id,
                topic="learning.improvement_detected",
                payload={
                    "model_type": model_type,
                    "improvement": improvement,
                    "new_accuracy": new_baseline
                }
            ))

            logger.info(f"Performance improvement for {model_type}: {improvement:+.3f}")

    def add_labeled_samples(self, labeled_data: List[tuple], model_type: str = "sentiment"):
        count = self.active_learner.update_with_labels(labeled_data)

        self.message_bus.publish(Message(
            type=MessageType.EVENT,
            sender=self.agent_id,
            topic="data.new_labeled",
            payload={
                "data_size": count,
                "model_type": model_type
            }
        ))

        logger.info(f"Added {count} newly labeled samples for {model_type}")

    def get_learning_status(self) -> Dict[str, Any]:
        time_to_next = self.learning_cycle_interval - (datetime.now() - self.last_learning_cycle)

        return {
            "last_cycle": self.last_learning_cycle.isoformat(),
            "next_cycle_in": str(time_to_next) if time_to_next.total_seconds() > 0 else "due_now",
            "performance_baseline": self.performance_baseline,
            "recent_improvements": self.improvement_log[-5:],
            "uncertain_samples": self.active_learner.get_statistics(),
            "training_queue": self.auto_trainer.get_training_statistics()
        }

    def force_learning_cycle(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        logger.info("Forcing learning cycle")
        self.last_learning_cycle = datetime.now() - self.learning_cycle_interval
        return self.check_and_trigger_learning_cycle(df)

    def configure_learning_interval(self, hours: int):
        self.learning_cycle_interval = timedelta(hours=hours)
        logger.info(f"Learning cycle interval set to {hours} hours")

    def get_improvement_summary(self) -> Dict[str, Any]:
        if not self.improvement_log:
            return {
                "total_improvements": 0,
                "avg_improvement": 0.0,
                "best_improvement": None
            }

        improvements = [log['improvement'] for log in self.improvement_log]

        return {
            "total_improvements": len(self.improvement_log),
            "avg_improvement": float(np.mean(improvements)),
            "best_improvement": max(self.improvement_log, key=lambda x: x['improvement']),
            "recent_log": self.improvement_log[-10:]
        }
