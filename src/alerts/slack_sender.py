import requests
import json
from config.settings import SLACK_WEBHOOK_URL
from src.utils.logger import default_logger as logger

def send_slack_alert(message, details=None):
    if not SLACK_WEBHOOK_URL:
        logger.warning("Slack webhook URL not configured, skipping Slack alert")
        return False

    try:
        payload = {
            "text": message,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Bank Text Analysis Alert"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Alert:* {message}"
                    }
                }
            ]
        }

        if details:
            detail_text = "\n".join([f"• *{k}:* {v}" for k, v in details.items()])
            payload["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details:*\n{detail_text}"
                }
            })

        response = requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            logger.info("Slack alert sent successfully")
            return True
        else:
            logger.error(f"Slack alert failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")
        return False

def send_anomaly_slack_alert(anomalies):
    if not anomalies:
        return False

    message = f"Detected {len(anomalies)} anomalies"

    details = {}
    for i, anomaly in enumerate(anomalies, 1):
        details[f"Anomaly {i}"] = f"{anomaly.get('type')}: {anomaly.get('message')}"

    return send_slack_alert(message, details)
