import requests
import json
from config.settings import JIRA_URL, JIRA_USER, JIRA_TOKEN, JIRA_PROJECT
from src.utils.logger import default_logger as logger

def create_jira_ticket(summary, description, priority="Medium"):
    if not JIRA_URL or not JIRA_USER or not JIRA_TOKEN:
        logger.warning("Jira credentials not configured, skipping ticket creation")
        return False

    try:
        url = f"{JIRA_URL}/rest/api/2/issue"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "fields": {
                "project": {
                    "key": JIRA_PROJECT
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": "Task"
                },
                "priority": {
                    "name": priority
                }
            }
        }

        response = requests.post(
            url,
            auth=(JIRA_USER, JIRA_TOKEN),
            headers=headers,
            data=json.dumps(payload)
        )

        if response.status_code == 201:
            issue_key = response.json().get("key")
            logger.info(f"Jira ticket created: {issue_key}")
            return issue_key
        else:
            logger.error(f"Failed to create Jira ticket: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error creating Jira ticket: {e}")
        return False

def create_anomaly_ticket(anomalies):
    if not anomalies:
        return False

    summary = f"[Auto] Anomaly Detected in Bank Text Analysis - {len(anomalies)} issues"

    description = "Automated ticket created by Bank Text Analysis system.\n\n"
    description += "Anomalies detected:\n"

    for i, anomaly in enumerate(anomalies, 1):
        description += f"\n{i}. Type: {anomaly.get('type', 'unknown')}\n"
        description += f"   Message: {anomaly.get('message', 'no details')}\n"
        if 'score' in anomaly:
            description += f"   Score: {anomaly['score']:.3f}\n"

    description += "\nPlease investigate and take appropriate action."

    priority = "High" if len(anomalies) >= 3 else "Medium"

    return create_jira_ticket(summary, description, priority)
