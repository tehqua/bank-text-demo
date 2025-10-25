import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime
from config.settings import TOPIC_MODEL_DIR, SENTIMENT_MODEL_DIR, RAW_DIR

TOOLS_DEFINITION = [
    {
        "name": "query_analysis_data",
        "description": "Query and analyze the current comment analysis data. Can filter by topic, sentiment, date range.",
        "parameters": {
            "query": "Natural language query about the data",
            "filter_topic": "Optional topic to filter",
            "filter_sentiment": "Optional sentiment to filter"
        }
    },
    {
        "name": "get_summary_stats",
        "description": "Get summary statistics about analyzed comments including total count, sentiment distribution, top topics.",
        "parameters": {}
    },
    {
        "name": "clean_models",
        "description": "Delete trained models to force retrain. Can specify 'topic', 'sentiment', or 'all'.",
        "parameters": {
            "model_type": "Type of model to clean: 'topic', 'sentiment', or 'all'"
        }
    },
    {
        "name": "get_top_issues",
        "description": "Get top negative issues from the analysis data.",
        "parameters": {
            "limit": "Number of top issues to return (default 5)"
        }
    },
    {
        "name": "check_anomalies",
        "description": "Run anomaly detection and drift analysis on current data.",
        "parameters": {}
    },
    {
        "name": "train_sentiment_model",
        "description": "Train sentiment classification model from labeled data file path.",
        "parameters": {
            "file_path": "Path to labeled CSV file with columns: comment, sentiment_label"
        }
    },
    {
        "name": "train_topic_model",
        "description": "Train topic classification model from labeled data file path.",
        "parameters": {
            "file_path": "Path to labeled CSV file with columns: comment, topic_label"
        }
    },
    {
        "name": "export_report",
        "description": "Export analysis report to CSV or JSON format.",
        "parameters": {
            "format": "Export format: 'csv' or 'json'",
            "filename": "Optional custom filename"
        }
    },
    {
        "name": "create_alert",
        "description": "Create alert/notification about issues found in analysis.",
        "parameters": {
            "alert_type": "Type of alert: 'email', 'slack', or 'log'",
            "message": "Alert message content"
        }
    },
    {
        "name": "run_full_analysis",
        "description": "Run complete analysis on a CSV file (load, preprocess, analyze topics & sentiment).",
        "parameters": {
            "file_path": "Path to CSV file to analyze"
        }
    }
]

class ChatbotTools:
    def __init__(self, df_pandas=None):
        self.df_pandas = df_pandas

    def query_analysis_data(self, query, filter_topic=None, filter_sentiment=None):
        if self.df_pandas is None or self.df_pandas.empty:
            return "No data available. Please upload and analyze data first."

        df = self.df_pandas.copy()

        if filter_topic and filter_topic != "All":
            df = df[df['topic_label'] == filter_topic]

        if filter_sentiment and filter_sentiment != "All":
            df = df[df['sentiment_label'] == filter_sentiment]

        if df.empty:
            return "No data matches the filters."

        summary = f"Found {len(df)} comments.\n\n"

        if 'topic_label' in df.columns:
            topic_counts = df['topic_label'].value_counts()
            summary += "Top topics:\n"
            for topic, count in topic_counts.head(5).items():
                summary += f"- {topic}: {count} comments\n"

        if 'sentiment_label' in df.columns:
            sentiment_counts = df['sentiment_label'].value_counts()
            summary += "\nSentiment distribution:\n"
            for sentiment, count in sentiment_counts.items():
                summary += f"- {sentiment}: {count}\n"

        return summary

    def get_summary_stats(self):
        if self.df_pandas is None or self.df_pandas.empty:
            return "No data available."

        df = self.df_pandas

        stats = {
            "total_comments": len(df),
            "unique_topics": df['topic_label'].nunique() if 'topic_label' in df.columns else 0,
            "avg_sentiment": df['sentiment_score'].mean() if 'sentiment_score' in df.columns else 0
        }

        result = f"📊 Summary Statistics:\n"
        result += f"- Total comments: {stats['total_comments']}\n"
        result += f"- Unique topics: {stats['unique_topics']}\n"
        result += f"- Average sentiment score: {stats['avg_sentiment']:.2f}\n"

        if 'sentiment_label' in df.columns:
            negative_count = df[df['sentiment_label'].isin(['Negative', 'Very Negative'])].shape[0]
            negative_ratio = negative_count / len(df) * 100
            result += f"- Negative comments: {negative_count} ({negative_ratio:.1f}%)\n"

        return result

    def clean_models(self, model_type="all"):
        results = []

        if model_type in ["topic", "all"]:
            topic_path = TOPIC_MODEL_DIR / "topic_auto"
            if topic_path.exists():
                shutil.rmtree(topic_path)
                results.append("✅ Topic models cleaned")
            else:
                results.append("ℹ️ No topic models found")

        if model_type in ["sentiment", "all"]:
            sentiment_path = SENTIMENT_MODEL_DIR / "sentiment_model"
            if sentiment_path.exists():
                shutil.rmtree(sentiment_path)
                results.append("✅ Sentiment models cleaned")
            else:
                results.append("ℹ️ No sentiment models found")

        return "\n".join(results)

    def get_top_issues(self, limit=5):
        if self.df_pandas is None or self.df_pandas.empty:
            return "No data available."

        df = self.df_pandas

        if 'sentiment_label' not in df.columns:
            return "Sentiment analysis not available."

        negative_df = df[df['sentiment_label'].isin(['Negative', 'Very Negative'])]

        if negative_df.empty:
            return "No negative comments found."

        result = f"🚨 Top {limit} Negative Issues:\n\n"

        for i, row in negative_df.head(limit).iterrows():
            topic = row.get('topic_label', 'Unknown')
            sentiment = row.get('sentiment_label', 'Unknown')
            comment = row.get('comment', '')[:100]
            result += f"{i+1}. Topic: {topic} | Sentiment: {sentiment}\n"
            result += f"   Comment: {comment}...\n\n"

        return result

    def check_anomalies(self):
        if self.df_pandas is None or self.df_pandas.empty:
            return "No data available."

        from src.agents.monitor import Monitor

        monitor = Monitor()
        current_metrics = monitor.calculate_current_metrics(self.df_pandas)
        anomalies = monitor.detect_anomalies(current_metrics)

        if not anomalies:
            return "✅ No anomalies detected. System is healthy."

        result = f"⚠️ Detected {len(anomalies)} anomalies:\n\n"
        for anomaly in anomalies:
            result += f"- {anomaly['type']}: {anomaly['message']}\n"

        return result

    def train_sentiment_model(self, file_path):
        try:
            from src.models.trainer import train_sentiment_model

            df = pd.read_csv(file_path)

            if 'comment' not in df.columns or 'sentiment_label' not in df.columns:
                return "❌ CSV must have 'comment' and 'sentiment_label' columns"

            texts = df['comment'].fillna("").tolist()
            labels = df['sentiment_label'].tolist()

            model, metrics = train_sentiment_model(texts, labels, log_mlflow=False)

            result = f"✅ Sentiment model trained successfully!\n"
            result += f"- Accuracy: {metrics.get('accuracy', 0):.3f}\n"
            result += f"- F1 Macro: {metrics.get('f1_macro', 0):.3f}\n"
            result += f"- F1 Weighted: {metrics.get('f1_weighted', 0):.3f}\n"

            return result

        except Exception as e:
            return f"❌ Error training sentiment model: {str(e)}"

    def train_topic_model(self, file_path):
        try:
            from src.models.trainer import train_topic_supervised_model

            df = pd.read_csv(file_path)

            if 'comment' not in df.columns or 'topic_label' not in df.columns:
                return "❌ CSV must have 'comment' and 'topic_label' columns"

            texts = df['comment'].fillna("").tolist()
            labels = df['topic_label'].tolist()

            model, metrics = train_topic_supervised_model(texts, labels, log_mlflow=False)

            result = f"✅ Topic model trained successfully!\n"
            result += f"- Accuracy: {metrics.get('accuracy', 0):.3f}\n"
            result += f"- F1 Macro: {metrics.get('f1_macro', 0):.3f}\n"

            return result

        except Exception as e:
            return f"❌ Error training topic model: {str(e)}"

    def export_report(self, format="csv", filename=None):
        if self.df_pandas is None or self.df_pandas.empty:
            return "No data available to export."

        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analysis_report_{timestamp}"

            if format == "csv":
                output_path = RAW_DIR / f"{filename}.csv"
                self.df_pandas.to_csv(output_path, index=False, encoding='utf-8-sig')
                return f"✅ Report exported to: {output_path}"

            elif format == "json":
                from src.utils.export import export_summary_to_json

                summary = {
                    "total_comments": len(self.df_pandas),
                    "unique_topics": self.df_pandas['topic_label'].nunique() if 'topic_label' in self.df_pandas.columns else 0,
                    "avg_sentiment": float(self.df_pandas['sentiment_score'].mean()) if 'sentiment_score' in self.df_pandas.columns else 0,
                    "sentiment_dist": self.df_pandas['sentiment_label'].value_counts().to_dict() if 'sentiment_label' in self.df_pandas.columns else {},
                    "topic_dist": self.df_pandas['topic_label'].value_counts().to_dict() if 'topic_label' in self.df_pandas.columns else {}
                }

                output_path = RAW_DIR / f"{filename}.json"
                export_summary_to_json(summary, output_path)
                return f"✅ Report exported to: {output_path}"

            else:
                return f"❌ Unsupported format: {format}. Use 'csv' or 'json'."

        except Exception as e:
            return f"❌ Error exporting report: {str(e)}"

    def create_alert(self, alert_type="log", message=""):
        try:
            if alert_type == "email":
                from src.alerts.email_sender import send_alert_email
                success = send_alert_email("Alert from Chatbot", message)
                if success:
                    return "✅ Email alert sent successfully!"
                else:
                    return "⚠️ Email not configured. Check .env settings."

            elif alert_type == "slack":
                from src.alerts.slack_sender import send_slack_alert
                success = send_slack_alert(message)
                if success:
                    return "✅ Slack alert sent successfully!"
                else:
                    return "⚠️ Slack webhook not configured. Check .env settings."

            elif alert_type == "log":
                from src.utils.logger import default_logger as logger
                logger.warning(f"CHATBOT ALERT: {message}")
                return f"✅ Alert logged:\n{message}"

            else:
                return f"❌ Unknown alert type: {alert_type}. Use 'email', 'slack', or 'log'."

        except Exception as e:
            return f"❌ Error creating alert: {str(e)}"

    def run_full_analysis(self, file_path):
        try:
            from src.etl.loader import load_and_validate
            from src.etl.preprocessor import preprocess_dataframe
            from src.models.topic.auto_topic import AutoTopicModel
            from src.models.sentiment.classifier import SentimentClassifier
            from src.models.sentiment.fallback import fallback_predict
            from src.models.trainer import train_topic_auto_model

            result = f"🔄 Starting analysis on {file_path}...\n\n"

            df = load_and_validate(file_path)
            result += f"✅ Step 1: Loaded {len(df)} comments\n"

            df = preprocess_dataframe(df)
            result += f"✅ Step 2: Preprocessed data\n"

            texts = df['comment_lower'].tolist()

            topic_path = TOPIC_MODEL_DIR / "topic_auto"
            if topic_path.exists():
                topic_model = AutoTopicModel.load(topic_path)
            else:
                result += "⚙️ Training new topic model...\n"
                topic_model = train_topic_auto_model(texts, n_clusters=5, log_mlflow=False)

            topic_labels, _ = topic_model.predict(texts)
            result += f"✅ Step 3: Topic analysis complete\n"

            sentiment_path = SENTIMENT_MODEL_DIR / "sentiment_model"
            if sentiment_path.exists():
                sentiment_model = SentimentClassifier.load(sentiment_path)
                sentiment_labels, sentiment_scores, _ = sentiment_model.predict_with_scores(texts)
            else:
                result += "⚙️ Using fallback sentiment analysis...\n"
                sentiment_labels, sentiment_scores = fallback_predict(texts)

            result += f"✅ Step 4: Sentiment analysis complete\n\n"

            df['topic_label'] = topic_labels
            df['sentiment_label'] = sentiment_labels
            df['sentiment_score'] = sentiment_scores

            self.df_pandas = df

            result += f"📊 Analysis Summary:\n"
            result += f"- Total comments: {len(df)}\n"
            result += f"- Unique topics: {df['topic_label'].nunique()}\n"
            result += f"- Avg sentiment: {df['sentiment_score'].mean():.2f}\n"

            negative_count = df[df['sentiment_label'].isin(['Negative', 'Very Negative'])].shape[0]
            result += f"- Negative comments: {negative_count} ({negative_count/len(df)*100:.1f}%)\n"

            return result

        except Exception as e:
            return f"❌ Error running analysis: {str(e)}"

    def execute_tool(self, tool_name, parameters):
        if tool_name == "query_analysis_data":
            return self.query_analysis_data(
                parameters.get("query", ""),
                parameters.get("filter_topic"),
                parameters.get("filter_sentiment")
            )
        elif tool_name == "get_summary_stats":
            return self.get_summary_stats()
        elif tool_name == "clean_models":
            return self.clean_models(parameters.get("model_type", "all"))
        elif tool_name == "get_top_issues":
            return self.get_top_issues(int(parameters.get("limit", 5)))
        elif tool_name == "check_anomalies":
            return self.check_anomalies()
        elif tool_name == "train_sentiment_model":
            return self.train_sentiment_model(parameters.get("file_path"))
        elif tool_name == "train_topic_model":
            return self.train_topic_model(parameters.get("file_path"))
        elif tool_name == "export_report":
            return self.export_report(
                parameters.get("format", "csv"),
                parameters.get("filename")
            )
        elif tool_name == "create_alert":
            return self.create_alert(
                parameters.get("alert_type", "log"),
                parameters.get("message", "")
            )
        elif tool_name == "run_full_analysis":
            return self.run_full_analysis(parameters.get("file_path"))
        else:
            return f"Unknown tool: {tool_name}"
