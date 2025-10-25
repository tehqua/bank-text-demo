import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, ALERT_EMAIL
from src.utils.logger import default_logger as logger

def send_alert_email(subject, body, to_email=None):
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured, skipping email")
        return False

    to_email = to_email or ALERT_EMAIL
    if not to_email:
        logger.warning("No recipient email configured")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()

        logger.info(f"Email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def create_alert_html(title, summary, details=None):
    html = f"""
    <html>
    <body>
        <h2>{title}</h2>
        <p>{summary}</p>
    """

    if details:
        html += "<h3>Details:</h3><ul>"
        for key, value in details.items():
            html += f"<li><strong>{key}:</strong> {value}</li>"
        html += "</ul>"

    html += """
    <p>---<br>
    Bank Text Analysis System<br>
    Auto-generated alert</p>
    </body>
    </html>
    """

    return html

def send_anomaly_alert(anomalies):
    if not anomalies:
        return False

    summary = f"Detected {len(anomalies)} anomalies in the system"
    details = {}

    for i, anomaly in enumerate(anomalies, 1):
        details[f"Anomaly {i}"] = f"{anomaly.get('type', 'unknown')}: {anomaly.get('message', 'no details')}"

    html_body = create_alert_html("System Anomaly Alert", summary, details)

    return send_alert_email("Anomaly Detected - Bank Text Analysis", html_body)
