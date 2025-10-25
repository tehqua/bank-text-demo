from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import numpy as np

def calculate_classification_metrics(y_true, y_pred, labels=None):
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1_macro": f1_score(y_true, y_pred, average='macro', zero_division=0),
        "f1_weighted": f1_score(y_true, y_pred, average='weighted', zero_division=0)
    }

    if labels:
        report = classification_report(y_true, y_pred, labels=labels, target_names=labels,
                                      output_dict=True, zero_division=0)
        metrics["per_class"] = report

    return metrics

def calculate_topic_coherence_score(texts, topic_labels):
    unique_topics = set(topic_labels)
    if len(unique_topics) <= 1:
        return 0.0

    topic_word_sets = {}
    for text, topic in zip(texts, topic_labels):
        if topic not in topic_word_sets:
            topic_word_sets[topic] = set()
        words = text.lower().split()
        topic_word_sets[topic].update(words[:20])

    coherence_scores = []
    topics = list(topic_word_sets.keys())
    for i in range(len(topics)):
        for j in range(i+1, len(topics)):
            intersection = len(topic_word_sets[topics[i]] & topic_word_sets[topics[j]])
            union = len(topic_word_sets[topics[i]] | topic_word_sets[topics[j]])
            if union > 0:
                coherence_scores.append(1 - intersection / union)

    return np.mean(coherence_scores) if coherence_scores else 0.5

def detect_drift(baseline_dist, current_dist, threshold=0.15):
    baseline_arr = np.array(list(baseline_dist.values()))
    current_arr = np.array(list(current_dist.values()))

    baseline_arr = baseline_arr / baseline_arr.sum() if baseline_arr.sum() > 0 else baseline_arr
    current_arr = current_arr / current_arr.sum() if current_arr.sum() > 0 else current_arr

    drift_score = np.sum(np.abs(baseline_arr - current_arr)) / 2

    return drift_score > threshold, drift_score

def detect_negative_spike(current_negative_ratio, baseline_negative_ratio, threshold=0.2):
    delta = current_negative_ratio - baseline_negative_ratio
    return delta > threshold, delta
