import numpy as np
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from src.utils.logger import default_logger as logger

@dataclass
class UncertaintySample:
    index: int
    text: str
    uncertainty_score: float
    predicted_label: str
    confidence_scores: Dict[str, float]

class ActiveLearner:
    def __init__(self, uncertainty_threshold: float = 0.3):
        self.uncertainty_threshold = uncertainty_threshold
        self.uncertain_samples: List[UncertaintySample] = []
        logger.info("ActiveLearner initialized")

    def identify_uncertain_samples(self, texts: List[str], predictions: List[str],
                                   probabilities: np.ndarray, top_k: int = 20) -> List[UncertaintySample]:
        uncertain_samples = []

        for idx, (text, pred, probs) in enumerate(zip(texts, predictions, probabilities)):
            max_prob = np.max(probs)
            uncertainty_score = 1.0 - max_prob

            if uncertainty_score >= self.uncertainty_threshold:
                confidence_scores = {f"class_{i}": float(p) for i, p in enumerate(probs)}

                sample = UncertaintySample(
                    index=idx,
                    text=text,
                    uncertainty_score=uncertainty_score,
                    predicted_label=pred,
                    confidence_scores=confidence_scores
                )
                uncertain_samples.append(sample)

        uncertain_samples.sort(key=lambda x: x.uncertainty_score, reverse=True)

        self.uncertain_samples = uncertain_samples[:top_k]
        logger.info(f"Identified {len(self.uncertain_samples)} uncertain samples")

        return self.uncertain_samples

    def margin_sampling(self, probabilities: np.ndarray, texts: List[str], predictions: List[str],
                       top_k: int = 20) -> List[UncertaintySample]:
        margins = []

        for probs in probabilities:
            sorted_probs = np.sort(probs)[::-1]
            margin = sorted_probs[0] - sorted_probs[1] if len(sorted_probs) > 1 else sorted_probs[0]
            margins.append(margin)

        margins = np.array(margins)
        uncertain_indices = np.argsort(margins)[:top_k]

        uncertain_samples = []
        for idx in uncertain_indices:
            confidence_scores = {f"class_{i}": float(p) for i, p in enumerate(probabilities[idx])}

            sample = UncertaintySample(
                index=int(idx),
                text=texts[idx],
                uncertainty_score=1.0 - margins[idx],
                predicted_label=predictions[idx],
                confidence_scores=confidence_scores
            )
            uncertain_samples.append(sample)

        self.uncertain_samples = uncertain_samples
        logger.info(f"Margin sampling identified {len(uncertain_samples)} samples")

        return uncertain_samples

    def entropy_sampling(self, probabilities: np.ndarray, texts: List[str], predictions: List[str],
                        top_k: int = 20) -> List[UncertaintySample]:
        entropies = []

        for probs in probabilities:
            probs = probs + 1e-10
            entropy = -np.sum(probs * np.log(probs))
            entropies.append(entropy)

        entropies = np.array(entropies)
        uncertain_indices = np.argsort(entropies)[::-1][:top_k]

        uncertain_samples = []
        for idx in uncertain_indices:
            confidence_scores = {f"class_{i}": float(p) for i, p in enumerate(probabilities[idx])}

            sample = UncertaintySample(
                index=int(idx),
                text=texts[idx],
                uncertainty_score=entropies[idx],
                predicted_label=predictions[idx],
                confidence_scores=confidence_scores
            )
            uncertain_samples.append(sample)

        self.uncertain_samples = uncertain_samples
        logger.info(f"Entropy sampling identified {len(uncertain_samples)} samples")

        return uncertain_samples

    def get_samples_for_labeling(self) -> List[Dict[str, Any]]:
        return [
            {
                "index": sample.index,
                "text": sample.text,
                "predicted_label": sample.predicted_label,
                "uncertainty_score": sample.uncertainty_score,
                "confidence_scores": sample.confidence_scores
            }
            for sample in self.uncertain_samples
        ]

    def update_with_labels(self, labeled_data: List[Tuple[int, str]]) -> int:
        labeled_indices = {idx for idx, _ in labeled_data}

        self.uncertain_samples = [
            sample for sample in self.uncertain_samples
            if sample.index not in labeled_indices
        ]

        logger.info(f"Updated uncertain samples, {len(labeled_data)} samples labeled")
        return len(labeled_data)

    def get_statistics(self) -> Dict[str, Any]:
        if not self.uncertain_samples:
            return {
                "total_uncertain": 0,
                "avg_uncertainty": 0.0,
                "max_uncertainty": 0.0,
                "min_uncertainty": 0.0
            }

        uncertainties = [s.uncertainty_score for s in self.uncertain_samples]

        return {
            "total_uncertain": len(self.uncertain_samples),
            "avg_uncertainty": float(np.mean(uncertainties)),
            "max_uncertainty": float(np.max(uncertainties)),
            "min_uncertainty": float(np.min(uncertainties))
        }
