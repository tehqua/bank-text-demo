from pathlib import Path
from src.models.sentiment.classifier import SentimentClassifier
from src.models.topic.supervised_topic import SupervisedTopicModel
from src.models.topic.auto_topic import AutoTopicModel
from src.utils.metrics import calculate_classification_metrics
from src.utils.logger import default_logger as logger
import mlflow
from config.settings import SENTIMENT_MODEL_DIR, TOPIC_MODEL_DIR, MLFLOW_TRACKING_URI

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

def train_sentiment_model(texts, labels, model_name="sentiment_model", log_mlflow=True):
    if len(texts) < 3:
        raise ValueError(f"Need at least 3 samples to train, got {len(texts)}")

    if len(set(labels)) < 2:
        raise ValueError("Need at least 2 different labels to train classifier")

    model = SentimentClassifier()
    model.fit(texts, labels)

    predictions, _ = model.predict(texts)
    metrics = calculate_classification_metrics(labels, predictions, list(model.classes_))

    if log_mlflow:
        try:
            mlflow.set_experiment("sentiment_training")
            with mlflow.start_run():
                mlflow.log_params({"n_samples": len(texts), "n_classes": len(model.classes_)})
                mlflow.log_metrics({
                    "accuracy": metrics["accuracy"],
                    "f1_macro": metrics["f1_macro"],
                    "f1_weighted": metrics["f1_weighted"]
                })

                model.save(SENTIMENT_MODEL_DIR / model_name)
                mlflow.log_artifacts(str(SENTIMENT_MODEL_DIR / model_name))
                logger.info(f"Sentiment model trained with MLflow, accuracy: {metrics['accuracy']:.3f}")
        except Exception as e:
            logger.warning(f"MLflow logging failed: {e}, continuing without MLflow")
            model.save(SENTIMENT_MODEL_DIR / model_name)
    else:
        model.save(SENTIMENT_MODEL_DIR / model_name)
        logger.info(f"Sentiment model trained (no MLflow), accuracy: {metrics['accuracy']:.3f}")

    return model, metrics

def train_topic_supervised_model(texts, labels, model_name="topic_supervised", log_mlflow=True):
    if len(texts) < 3:
        raise ValueError(f"Need at least 3 samples to train, got {len(texts)}")

    if len(set(labels)) < 2:
        raise ValueError("Need at least 2 different labels to train classifier")

    model = SupervisedTopicModel()
    model.fit(texts, labels)

    predictions, _ = model.predict(texts)
    metrics = calculate_classification_metrics(labels, predictions, list(model.classes_))

    if log_mlflow:
        try:
            mlflow.set_experiment("topic_training")
            with mlflow.start_run():
                mlflow.log_params({"n_samples": len(texts), "n_classes": len(model.classes_)})
                mlflow.log_metrics({
                    "accuracy": metrics["accuracy"],
                    "f1_macro": metrics["f1_macro"]
                })

                model.save(TOPIC_MODEL_DIR / model_name)
                mlflow.log_artifacts(str(TOPIC_MODEL_DIR / model_name))
                logger.info(f"Topic model trained with MLflow, accuracy: {metrics['accuracy']:.3f}")
        except Exception as e:
            logger.warning(f"MLflow logging failed: {e}, continuing without MLflow")
            model.save(TOPIC_MODEL_DIR / model_name)
    else:
        model.save(TOPIC_MODEL_DIR / model_name)
        logger.info(f"Topic model trained (no MLflow), accuracy: {metrics['accuracy']:.3f}")

    return model, metrics

def train_topic_auto_model(texts, n_clusters=8, model_name="topic_auto", log_mlflow=True):
    if log_mlflow:
        mlflow.set_experiment("topic_auto_training")
        with mlflow.start_run():
            model = AutoTopicModel(n_clusters=n_clusters)
            model.fit(texts)

            mlflow.log_params({"n_samples": len(texts), "n_clusters": n_clusters})

            model.save(TOPIC_MODEL_DIR / model_name)
            mlflow.log_artifacts(str(TOPIC_MODEL_DIR / model_name))

            logger.info(f"Auto topic model trained with {n_clusters} clusters")
            return model
    else:
        model = AutoTopicModel(n_clusters=n_clusters)
        model.fit(texts)
        model.save(TOPIC_MODEL_DIR / model_name)
        logger.info("Auto topic model trained (no MLflow)")
        return model
