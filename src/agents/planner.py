from datetime import datetime
from src.utils.logger import default_logger as logger

class Planner:
    def __init__(self):
        self.action_templates = {
            "retrain_sentiment": {
                "description": "Retrain sentiment model due to accuracy drop",
                "steps": [
                    "collect_labeled_data",
                    "train_sentiment_model",
                    "evaluate_model",
                    "deploy_if_improved"
                ]
            },
            "retrain_topic": {
                "description": "Retrain topic model due to drift",
                "steps": [
                    "collect_recent_comments",
                    "train_topic_model",
                    "evaluate_coherence",
                    "update_model"
                ]
            },
            "alert_ops": {
                "description": "Send alert to operations team",
                "steps": [
                    "prepare_summary",
                    "send_email",
                    "send_slack",
                    "create_ticket"
                ]
            },
            "analyze_spike": {
                "description": "Deep dive analysis on spike",
                "steps": [
                    "identify_affected_topics",
                    "extract_sample_comments",
                    "generate_report"
                ]
            }
        }

    def create_plan(self, violations, anomalies):
        plan = {
            "created_at": datetime.now().isoformat(),
            "violations": violations,
            "anomalies": anomalies,
            "actions": []
        }

        action_types = set()
        for violation in violations:
            action_type = violation.get("action")
            if action_type:
                action_types.add(action_type)

        for anomaly in anomalies:
            anomaly_type = anomaly.get("type")
            if "drift" in anomaly_type:
                if "sentiment" in anomaly_type:
                    action_types.add("retrain_sentiment")
                elif "topic" in anomaly_type:
                    action_types.add("retrain_topic")
            elif "spike" in anomaly_type:
                action_types.add("alert_ops")
                action_types.add("analyze_spike")

        for action_type in action_types:
            if action_type in self.action_templates:
                template = self.action_templates[action_type]
                plan["actions"].append({
                    "type": action_type,
                    "description": template["description"],
                    "steps": template["steps"],
                    "status": "pending"
                })

        logger.info(f"Plan created with {len(plan['actions'])} actions")
        return plan

    def prioritize_actions(self, plan):
        priority_order = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3
        }

        action_priority_map = {
            "alert_ops": "critical",
            "analyze_spike": "high",
            "retrain_sentiment": "high",
            "retrain_topic": "medium"
        }

        actions = plan["actions"]
        for action in actions:
            action["priority"] = action_priority_map.get(action["type"], "low")

        actions.sort(key=lambda x: priority_order.get(x["priority"], 99))

        plan["actions"] = actions
        return plan
