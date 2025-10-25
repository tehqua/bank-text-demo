from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path
from src.agents.message_bus import MessageBus, Message, MessageType, MessagePriority
from config.settings import MODEL_DIR
from src.utils.logger import default_logger as logger

@dataclass
class ModelMetrics:
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    timestamp: str = ""

@dataclass
class ModelCard:
    model_id: str
    model_name: str
    model_type: str
    version: str
    created_at: str
    updated_at: str
    status: str
    metrics: ModelMetrics
    training_data_size: int = 0
    hyperparameters: Dict[str, Any] = None
    deployment_status: str = "staging"
    performance_history: List[ModelMetrics] = None
    drift_score: float = 0.0
    retraining_count: int = 0
    last_retrain_trigger: str = ""

    def __post_init__(self):
        if self.hyperparameters is None:
            self.hyperparameters = {}
        if self.performance_history is None:
            self.performance_history = []

class ModelCardAgent:
    def __init__(self, agent_id: str = "ModelCardAgent"):
        self.agent_id = agent_id
        self.message_bus = MessageBus()
        self.model_cards: Dict[str, ModelCard] = {}
        self.cards_dir = MODEL_DIR / "cards"
        self.cards_dir.mkdir(parents=True, exist_ok=True)

        self._subscribe_to_events()
        self._load_existing_cards()
        logger.info(f"{self.agent_id} initialized")

    def _subscribe_to_events(self):
        self.message_bus.subscribe("model.trained", self.handle_model_trained)
        self.message_bus.subscribe("model.evaluated", self.handle_model_evaluated)
        self.message_bus.subscribe("model.deployed", self.handle_model_deployed)
        self.message_bus.subscribe("model.get_card", self.handle_get_card_request)
        self.message_bus.subscribe("model.update_metrics", self.handle_update_metrics)

    def _load_existing_cards(self):
        for card_file in self.cards_dir.glob("*.json"):
            try:
                with open(card_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metrics = ModelMetrics(**data['metrics'])
                    perf_history = [ModelMetrics(**m) for m in data.get('performance_history', [])]
                    data['metrics'] = metrics
                    data['performance_history'] = perf_history
                    card = ModelCard(**data)
                    self.model_cards[card.model_id] = card
                    logger.info(f"Loaded model card: {card.model_id}")
            except Exception as e:
                logger.error(f"Error loading card {card_file}: {e}")

    def create_model_card(self, model_name: str, model_type: str, metrics: Dict[str, float],
                          training_data_size: int, hyperparameters: Dict[str, Any]) -> ModelCard:
        model_id = f"{model_type}_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        now = datetime.now().isoformat()

        metrics_obj = ModelMetrics(
            accuracy=metrics.get('accuracy', 0.0),
            precision=metrics.get('precision', 0.0),
            recall=metrics.get('recall', 0.0),
            f1_score=metrics.get('f1_weighted', 0.0),
            timestamp=now
        )

        card = ModelCard(
            model_id=model_id,
            model_name=model_name,
            model_type=model_type,
            version="1.0.0",
            created_at=now,
            updated_at=now,
            status="active",
            metrics=metrics_obj,
            training_data_size=training_data_size,
            hyperparameters=hyperparameters,
            performance_history=[metrics_obj]
        )

        self.model_cards[model_id] = card
        self._save_card(card)

        self.message_bus.publish(Message(
            type=MessageType.EVENT,
            sender=self.agent_id,
            topic="model.card_created",
            payload={"model_id": model_id, "model_name": model_name}
        ))

        logger.info(f"Created model card: {model_id}")
        return card

    def update_metrics(self, model_id: str, new_metrics: Dict[str, float]):
        if model_id not in self.model_cards:
            logger.warning(f"Model card not found: {model_id}")
            return

        card = self.model_cards[model_id]
        now = datetime.now().isoformat()

        new_metrics_obj = ModelMetrics(
            accuracy=new_metrics.get('accuracy', 0.0),
            precision=new_metrics.get('precision', 0.0),
            recall=new_metrics.get('recall', 0.0),
            f1_score=new_metrics.get('f1_weighted', 0.0),
            timestamp=now
        )

        card.metrics = new_metrics_obj
        card.performance_history.append(new_metrics_obj)
        card.updated_at = now

        if self._detect_performance_degradation(card):
            self.message_bus.publish(Message(
                type=MessageType.EVENT,
                sender=self.agent_id,
                topic="model.degradation_detected",
                payload={
                    "model_id": model_id,
                    "current_accuracy": new_metrics_obj.accuracy,
                    "severity": "high" if new_metrics_obj.accuracy < 0.5 else "medium"
                },
                priority=MessagePriority.HIGH
            ))

        self._save_card(card)
        logger.info(f"Updated metrics for {model_id}")

    def _detect_performance_degradation(self, card: ModelCard) -> bool:
        if len(card.performance_history) < 2:
            return False

        current = card.performance_history[-1].accuracy
        previous = card.performance_history[-2].accuracy

        return current < previous * 0.9

    def handle_model_trained(self, message: Message):
        payload = message.payload
        self.create_model_card(
            model_name=payload.get('model_name', 'unknown'),
            model_type=payload.get('model_type', 'unknown'),
            metrics=payload.get('metrics', {}),
            training_data_size=payload.get('training_data_size', 0),
            hyperparameters=payload.get('hyperparameters', {})
        )

    def handle_model_evaluated(self, message: Message):
        payload = message.payload
        model_id = payload.get('model_id')
        new_metrics = payload.get('metrics', {})
        if model_id:
            self.update_metrics(model_id, new_metrics)

    def handle_model_deployed(self, message: Message):
        payload = message.payload
        model_id = payload.get('model_id')
        if model_id and model_id in self.model_cards:
            card = self.model_cards[model_id]
            card.deployment_status = "production"
            card.updated_at = datetime.now().isoformat()
            self._save_card(card)

    def handle_get_card_request(self, message: Message):
        model_id = message.payload.get('model_id')
        if model_id and model_id in self.model_cards:
            card = self.model_cards[model_id]
            self.message_bus.respond(message, {"card": self._card_to_dict(card)})
        else:
            self.message_bus.respond(message, {"error": "Model card not found"})

    def handle_update_metrics(self, message: Message):
        model_id = message.payload.get('model_id')
        metrics = message.payload.get('metrics', {})
        if model_id:
            self.update_metrics(model_id, metrics)

    def _save_card(self, card: ModelCard):
        card_file = self.cards_dir / f"{card.model_id}.json"
        try:
            with open(card_file, 'w', encoding='utf-8') as f:
                json.dump(self._card_to_dict(card), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving card {card.model_id}: {e}")

    def _card_to_dict(self, card: ModelCard) -> Dict:
        data = asdict(card)
        return data

    def get_all_cards(self) -> List[ModelCard]:
        return list(self.model_cards.values())

    def get_card_by_name(self, model_name: str) -> Optional[ModelCard]:
        for card in self.model_cards.values():
            if card.model_name == model_name:
                return card
        return None

    def get_performance_summary(self) -> Dict[str, Any]:
        summary = {
            "total_models": len(self.model_cards),
            "active_models": sum(1 for c in self.model_cards.values() if c.status == "active"),
            "production_models": sum(1 for c in self.model_cards.values() if c.deployment_status == "production"),
            "models": []
        }

        for card in self.model_cards.values():
            summary["models"].append({
                "model_id": card.model_id,
                "model_name": card.model_name,
                "model_type": card.model_type,
                "accuracy": card.metrics.accuracy,
                "f1_score": card.metrics.f1_score,
                "status": card.status,
                "deployment": card.deployment_status
            })

        return summary
