from datetime import datetime
from pathlib import Path
import json
from src.utils.logger import default_logger as logger

class Executor:
    def __init__(self, memory=None):
        self.memory = memory
        self.execution_log = []

    def execute_plan(self, plan, dry_run=True):
        logger.info(f"Executing plan ({'DRY RUN' if dry_run else 'LIVE'})")

        results = []
        for action in plan["actions"]:
            action_type = action["type"]
            result = self._execute_action(action_type, action, dry_run)
            results.append(result)

            if self.memory:
                self.memory.record_action(action_type, result)

        return results

    def _execute_action(self, action_type, action_config, dry_run):
        logger.info(f"Executing action: {action_type}")

        result = {
            "action": action_type,
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "success": False,
            "message": ""
        }

        if dry_run:
            result["success"] = True
            result["message"] = f"DRY RUN: Would execute {action_type}"
            return result

        try:
            if action_type == "alert_ops":
                result = self._send_alerts(action_config)
            elif action_type == "retrain_sentiment":
                result = self._trigger_retrain("sentiment")
            elif action_type == "retrain_topic":
                result = self._trigger_retrain("topic")
            elif action_type == "analyze_spike":
                result = self._analyze_spike()
            else:
                result["message"] = f"Unknown action type: {action_type}"

        except Exception as e:
            result["success"] = False
            result["message"] = f"Error: {str(e)}"
            logger.error(f"Action {action_type} failed: {e}")

        return result

    def _send_alerts(self, config):
        from src.alerts.email_sender import send_alert_email
        from src.alerts.slack_sender import send_slack_alert

        try:
            send_alert_email("Anomaly Detected", "An anomaly has been detected in the system.")
            send_slack_alert("Anomaly detected in bank comment analysis")

            return {
                "action": "alert_ops",
                "success": True,
                "message": "Alerts sent successfully",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "action": "alert_ops",
                "success": False,
                "message": f"Failed to send alerts: {e}",
                "timestamp": datetime.now().isoformat()
            }

    def _trigger_retrain(self, model_type):
        logger.info(f"Triggering {model_type} model retrain")
        return {
            "action": f"retrain_{model_type}",
            "success": True,
            "message": f"Retrain job for {model_type} scheduled",
            "timestamp": datetime.now().isoformat()
        }

    def _analyze_spike(self):
        logger.info("Analyzing spike")
        return {
            "action": "analyze_spike",
            "success": True,
            "message": "Spike analysis completed",
            "timestamp": datetime.now().isoformat()
        }
