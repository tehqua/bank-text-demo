from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import joblib
import numpy as np
from pathlib import Path
from config.model_config import TFIDF_CONFIG, TFIDF_CONFIG_SMALL, KMEANS_CONFIG, TOP_TERMS_PER_TOPIC
from src.utils.logger import default_logger as logger

class AutoTopicModel:
    def __init__(self, n_clusters=None):
        self.n_clusters = n_clusters or KMEANS_CONFIG["n_clusters"]
        self.vectorizer = None
        self.kmeans = None
        self.topic_labels = {}

    def fit(self, texts):
        n_samples = len(texts)

        if self.n_clusters > n_samples:
            self.n_clusters = max(2, n_samples // 2)
            logger.warning(f"Adjusted n_clusters to {self.n_clusters} (too few samples)")

        logger.info(f"Training auto topic model with {self.n_clusters} clusters")

        if n_samples < 10:
            logger.warning(f"Small dataset ({n_samples} samples), using TFIDF_CONFIG_SMALL")
            tfidf_config = TFIDF_CONFIG_SMALL.copy()
        else:
            tfidf_config = TFIDF_CONFIG.copy()

        self.vectorizer = TfidfVectorizer(**tfidf_config)

        kmeans_config = KMEANS_CONFIG.copy()
        kmeans_config["n_clusters"] = self.n_clusters
        self.kmeans = KMeans(**kmeans_config)

        X = self.vectorizer.fit_transform(texts)
        self.kmeans.fit(X)
        self._generate_topic_labels()
        logger.info("Auto topic model training complete")
        return self

    def _generate_topic_labels(self):
        feature_names = self.vectorizer.get_feature_names_out()
        for cluster_id in range(self.n_clusters):
            center = self.kmeans.cluster_centers_[cluster_id]
            top_indices = center.argsort()[-TOP_TERMS_PER_TOPIC:][::-1]

            unique_terms = []
            seen_words = set()

            for idx in top_indices:
                term = feature_names[idx]
                words_in_term = term.lower().split()

                is_duplicate = False
                for word in words_in_term:
                    if word in seen_words:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    unique_terms.append(term)
                    for word in words_in_term:
                        seen_words.add(word)

                if len(unique_terms) >= 3:
                    break

            if len(unique_terms) == 0:
                unique_terms = [feature_names[top_indices[0]]]

            self.topic_labels[cluster_id] = " ".join(unique_terms)

    def predict(self, texts):
        X = self.vectorizer.transform(texts)
        cluster_ids = self.kmeans.predict(X)
        topic_labels = [self.topic_labels.get(cid, f"Topic_{cid}") for cid in cluster_ids]
        return topic_labels, cluster_ids

    def save(self, model_dir):
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.vectorizer, model_dir / "vectorizer.pkl")
        joblib.dump(self.kmeans, model_dir / "kmeans.pkl")
        joblib.dump(self.topic_labels, model_dir / "topic_labels.pkl")
        logger.info(f"Auto topic model saved to {model_dir}")

    @classmethod
    def load(cls, model_dir):
        model_dir = Path(model_dir)
        model = cls()
        model.vectorizer = joblib.load(model_dir / "vectorizer.pkl")
        model.kmeans = joblib.load(model_dir / "kmeans.pkl")
        model.topic_labels = joblib.load(model_dir / "topic_labels.pkl")
        model.n_clusters = model.kmeans.n_clusters
        logger.info(f"Auto topic model loaded from {model_dir}")
        return model
