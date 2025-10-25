import json
from pathlib import Path
from datetime import datetime
from config.settings import KPI_SENTIMENT_ACCURACY_MIN, KPI_NEGATIVE_SPIKE_THRESHOLD, KPI_DRIFT_THRESHOLD
from src.utils.logger import default_logger as logger

class GoalManager:
    def __init__(self, config_path=None):
        self.config_path = config_path or Path("data/goals_config.json")
        self.goals = self._load_goals()

    def _load_goals(self):
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._default_goals()

    def _default_goals(self):
        return {
            "sentiment_accuracy": {
                "metric": "sentiment_accuracy",
                "threshold": KPI_SENTIMENT_ACCURACY_MIN,
                "operator": ">=",
                "priority": "high",
                "action": "retrain_sentiment"
            },
            "negative_spike": {
                "metric": "negative_ratio_delta",
                "threshold": KPI_NEGATIVE_SPIKE_THRESHOLD,
                "operator": ">",
                "priority": "critical",
                "action": "alert_ops"
            },
            "topic_drift": {
                "metric": "topic_drift_score",
                "threshold": KPI_DRIFT_THRESHOLD,
                "operator": ">",
                "priority": "medium",
                "action": "retrain_topic"
            }
        }

    def save_goals(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.goals, f, indent=2, ensure_ascii=False)
        logger.info(f"Goals saved to {self.config_path}")

    def check_goal_violations(self, metrics):
        violations = []

        for goal_name, goal_config in self.goals.items():
            metric_name = goal_config["metric"]
            threshold = goal_config["threshold"]
            operator = goal_config["operator"]

            if metric_name not in metrics:
                continue

            metric_value = metrics[metric_name]

            violated = False
            if operator == ">=" and metric_value < threshold:
                violated = True
            elif operator == ">" and metric_value > threshold:
                violated = True
            elif operator == "<=" and metric_value > threshold:
                violated = True
            elif operator == "<" and metric_value < threshold:
                violated = True

            if violated:
                violations.append({
                    "goal": goal_name,
                    "metric": metric_name,
                    "value": metric_value,
                    "threshold": threshold,
                    "priority": goal_config["priority"],
                    "action": goal_config["action"],
                    "timestamp": datetime.now().isoformat()
                })

        return violations

    def get_actions_for_violations(self, violations):
        actions = []
        for violation in violations:
            actions.append({
                "type": violation["action"],
                "priority": violation["priority"],
                "reason": f"{violation['metric']} = {violation['value']:.3f} (threshold: {violation['threshold']})",
                "violation": violation
            })
        return actions
