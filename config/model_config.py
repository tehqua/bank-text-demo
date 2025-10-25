TFIDF_CONFIG = {
    "max_features": 5000,
    "ngram_range": (1, 2),
    "min_df": 1,
    "max_df": 0.95,
    "sublinear_tf": True
}

TFIDF_CONFIG_SMALL = {
    "max_features": 1000,
    "ngram_range": (1, 1),
    "min_df": 1,
    "max_df": 1.0,
    "sublinear_tf": True
}

KMEANS_CONFIG = {
    "n_clusters": 8,
    "random_state": 42,
    "max_iter": 300,
    "n_init": 10
}

LOGISTIC_REGRESSION_CONFIG = {
    "max_iter": 500,
    "random_state": 42,
    "solver": "lbfgs",
    "multi_class": "multinomial",
    "C": 1.0
}

NAIVE_BAYES_CONFIG = {
    "alpha": 1.0
}

SENTIMENT_MODEL_NAME = "sentiment_lr_model"
TOPIC_AUTO_MODEL_NAME = "topic_kmeans_model"
TOPIC_SUPERVISED_MODEL_NAME = "topic_classifier_model"

TOP_TERMS_PER_TOPIC = 10
