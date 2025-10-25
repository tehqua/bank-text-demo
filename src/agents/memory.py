import json
from pathlib import Path
from datetime import datetime
from src.utils.logger import default_logger as logger

class Memory:
    def __init__(self, memory_path=None):
        self.memory_path = memory_path or Path("data/agent_memory.json")
        self.history = self._load_history()

    def _load_history(self):
        if self.memory_path.exists():
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"actions": [], "outcomes": []}

    def save_history(self):
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.memory_path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
        logger.info(f"Memory saved to {self.memory_path}")

    def record_action(self, action_type, result):
        record = {
            "action": action_type,
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "success": result.get("success", False)
        }

        self.history["actions"].append(record)
        self.save_history()
        logger.info(f"Action recorded: {action_type}")

    def record_outcome(self, action_id, metrics_before, metrics_after):
        outcome = {
            "action_id": action_id,
            "timestamp": datetime.now().isoformat(),
            "metrics_before": metrics_before,
            "metrics_after": metrics_after,
            "improvement": self._calculate_improvement(metrics_before, metrics_after)
        }

        self.history["outcomes"].append(outcome)
        self.save_history()
        logger.info(f"Outcome recorded for action {action_id}")

    def _calculate_improvement(self, before, after):
        improvement = {}

        if "sentiment_accuracy" in before and "sentiment_accuracy" in after:
            improvement["sentiment_accuracy"] = after["sentiment_accuracy"] - before["sentiment_accuracy"]

        if "negative_ratio" in before and "negative_ratio" in after:
            improvement["negative_ratio_reduction"] = before["negative_ratio"] - after["negative_ratio"]

        return improvement

    def get_recent_actions(self, n=10):
        return self.history["actions"][-n:]

    def get_all_actions(self):
        return self.history["actions"]

    def get_action_success_rate(self, action_type=None):
        actions = self.history["actions"]

        if action_type:
            actions = [a for a in actions if a["action"] == action_type]

        if not actions:
            return 0.0

        successes = sum(1 for a in actions if a.get("success", False))
        return successes / len(actions)

    def get_summary(self):
        total_actions = len(self.history["actions"])
        total_outcomes = len(self.history["outcomes"])

        success_rate = self.get_action_success_rate()

        return {
            "total_actions": total_actions,
            "total_outcomes": total_outcomes,
            "overall_success_rate": success_rate,
            "recent_actions": self.get_recent_actions(5)
        }
