from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
import joblib
from pathlib import Path
from config.model_config import TFIDF_CONFIG, TFIDF_CONFIG_SMALL, LOGISTIC_REGRESSION_CONFIG
from src.utils.logger import default_logger as logger

class SupervisedTopicModel:
    def __init__(self, model_type="logistic"):
        self.vectorizer = None
        if model_type == "logistic":
            self.classifier = LogisticRegression(**LOGISTIC_REGRESSION_CONFIG)
        else:
            from config.model_config import NAIVE_BAYES_CONFIG
            self.classifier = MultinomialNB(**NAIVE_BAYES_CONFIG)
        self.model_type = model_type
        self.classes_ = None

    def fit(self, texts, labels):
        logger.info(f"Training supervised topic model ({self.model_type})")

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
        logger.info(f"Supervised topic model trained, classes: {len(self.classes_)}")
        return self

    def predict(self, texts):
        X = self.vectorizer.transform(texts)
        predictions = self.classifier.predict(X)
        probabilities = self.classifier.predict_proba(X)
        return predictions, probabilities

    def save(self, model_dir):
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.vectorizer, model_dir / "vectorizer.pkl")
        joblib.dump(self.classifier, model_dir / "classifier.pkl")
        joblib.dump({"model_type": self.model_type, "classes": self.classes_},
                   model_dir / "metadata.pkl")
        logger.info(f"Supervised topic model saved to {model_dir}")

    @classmethod
    def load(cls, model_dir):
        model_dir = Path(model_dir)
        metadata = joblib.load(model_dir / "metadata.pkl")

        model = cls(model_type=metadata["model_type"])
        model.vectorizer = joblib.load(model_dir / "vectorizer.pkl")
        model.classifier = joblib.load(model_dir / "classifier.pkl")
        model.classes_ = metadata["classes"]
        logger.info(f"Supervised topic model loaded from {model_dir}")
        return model
