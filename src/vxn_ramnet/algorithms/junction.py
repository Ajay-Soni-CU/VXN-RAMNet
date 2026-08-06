from __future__ import annotations
from dataclasses import asdict, dataclass
import numpy as np
from vxn_ramnet.config.models import DetectionSettings
from vxn_ramnet.core.exceptions import InsufficientEvidenceError
from .similarity import window_similarity_score

@dataclass(frozen=True)
class JunctionCandidate:
    first_index: int
    return_index: int
    raw_score: float
    same_order_score: float
    reverse_order_score: float
    plausibility: float
    final_score: float

class ConstrainedJunctionDetector:
    """Detector for the documented single-junction backtracking experiment.

    This is intentionally not represented as a general route-graph detector.
    """
    def __init__(self, settings: DetectionSettings):
        self.settings = settings

    def detect(self, self_similarity: np.ndarray) -> tuple[JunctionCandidate, list[JunctionCandidate]]:
        matrix = np.asarray(self_similarity, dtype=np.float32)
        n = len(matrix)
        if matrix.ndim != 2 or matrix.shape != (n, n) or n < 30:
            raise InsufficientEvidenceError("At least 30 frames and a square self-similarity matrix are required")
        first_start, first_end = (int(r*n) for r in self.settings.first_junction_search)
        return_start, return_end = (int(r*n) for r in self.settings.return_junction_search)
        first_end = min(n, max(first_start + 1, first_end))
        return_end = min(n, max(return_start + 1, return_end))
        minimum_gap = max(1, int(self.settings.min_junction_gap_ratio*n))
        candidates: list[JunctionCandidate] = []
        for first in range(first_start, first_end):
            for returned in range(max(return_start, first+minimum_gap), return_end):
                score, same, reverse = window_similarity_score(matrix, first, returned, self.settings.junction_window)
                plausibility = max(0.0, 1.0
                    - abs(first/n-self.settings.expected_first_junction_ratio)*self.settings.plausibility_weight
                    - abs(returned/n-self.settings.expected_return_junction_ratio)*self.settings.plausibility_weight)
                candidates.append(JunctionCandidate(first, returned, score, same, reverse, plausibility, score*plausibility))
        if not candidates:
            raise InsufficientEvidenceError("No valid junction candidate exists inside configured search ranges")
        candidates.sort(key=lambda item: item.final_score, reverse=True)
        return candidates[0], candidates[:10]


def junction_confidence(score: float, settings: DetectionSettings) -> str:
    if score >= settings.good_junction_score:
        return "high"
    if score >= settings.acceptable_junction_score:
        return "review"
    return "low"


def candidate_to_dict(candidate: JunctionCandidate) -> dict:
    return asdict(candidate)
