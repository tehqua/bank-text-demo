from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import numpy as np
from pathlib import Path
from config.model_config import TFIDF_CONFIG, TFIDF_CONFIG_SMALL, LOGISTIC_REGRESSION_CONFIG
from config.settings import SENTIMENT_LABELS
from src.utils.logger import default_logger as logger

class SentimentClassifier:
    def __init__(self):
        self.vectorizer = None
        self.classifier = LogisticRegression(**LOGISTIC_REGRESSION_CONFIG)
        self.classes_ = None

    def fit(self, texts, labels):
        logger.info("Training sentiment classifier")

        n_samples = len(texts)
        if n_samples < 10:
            logger.warning(f"Small dataset ({n_samples} samples), using TFIDF_CONFIG_SMALL")
            tfidf_config = TFIDF_CONFIG_SMALL.copy()
        else:
            tfidf_config = TFIDF_CONFIG.copy()

        self.vectorizer = TfidfVectorizer(**tfidf_config)

        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)
        self.classes_ = self.classifier.classes_
        logger.info(f"Sentiment classifier trained, classes: {list(self.classes_)}")
        return self

    def predict(self, texts):
        X = self.vectorizer.transform(texts)
        predictions = self.classifier.predict(X)
        probabilities = self.classifier.predict_proba(X)
        max_probs = np.max(probabilities, axis=1)
        return predictions, max_probs

    def predict_with_scores(self, texts):
        predictions, probs = self.predict(texts)
        scores = self._convert_to_scores(predictions)
        return predictions, scores, probs

    def _convert_to_scores(self, labels):
        label_to_score = {
            "Very Negative": -2,
            "Negative": -1,
            "Neutral": 0,
            "Positive": 1,
            "Very Positive": 2,
            "Mixed": 0
        }
        scores = [label_to_score.get(label, 0) for label in labels]
        return scores

    def save(self, model_dir):
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.vectorizer, model_dir / "vectorizer.pkl")
        joblib.dump(self.classifier, model_dir / "classifier.pkl")
        joblib.dump({"classes": self.classes_}, model_dir / "metadata.pkl")
        logger.info(f"Sentiment classifier saved to {model_dir}")

    @classmethod
    def load(cls, model_dir):
        model_dir = Path(model_dir)
        model = cls()
        model.vectorizer = joblib.load(model_dir / "vectorizer.pkl")
        model.classifier = joblib.load(model_dir / "classifier.pkl")
        metadata = joblib.load(model_dir / "metadata.pkl")
        model.classes_ = metadata["classes"]
        logger.info(f"Sentiment classifier loaded from {model_dir}")
        return model
