from __future__ import annotations
from dataclasses import asdict, dataclass
import numpy as np
from vxn_ramnet.config.models import DetectionSettings
from vxn_ramnet.core.exceptions import InsufficientEvidenceError
from .similarity import flip_aware_similarity

@dataclass(frozen=True)
class TurnaroundCandidate:
    index: int
    raw_score: float
    balance: float
    final_score: float
    ratio: float

class ReverseSequenceTurnaroundDetector:
    def __init__(self, settings: DetectionSettings):
        self.settings = settings

    def _score(self, original: np.ndarray, flipped: np.ndarray, start: int, middle: int, end: int) -> float:
        if middle <= start + 4 or end <= middle + 4:
            return -1.0
        count = min(self.settings.reverse_sample_count, middle-start+1, end-middle+1)
        if count < 6:
            return -1.0
        left = np.linspace(start, middle, count, dtype=np.int64)
        right = np.linspace(middle, end, count, dtype=np.int64)[::-1]
        similarity = flip_aware_similarity(original[left], flipped[left], original[right], flipped[right], self.settings.self_similarity_chunk_size)
        return float(np.mean(np.diag(similarity)))

    def detect(self, original: np.ndarray, flipped: np.ndarray, first: int, returned: int) -> tuple[TurnaroundCandidate, list[TurnaroundCandidate]]:
        n = len(original)
        margin = max(8, int(0.08*n))
        search_start, search_end = first+margin, returned-margin
        if search_end <= search_start:
            raise InsufficientEvidenceError("Junction visits are too close to estimate a turnaround")
        gap = returned-first
        candidates: list[TurnaroundCandidate] = []
        for middle in range(search_start, search_end):
            score = self._score(original, flipped, first, middle, returned)
            ratio = (middle-first)/max(1, gap)
            balance = max(0.0, 1.0-abs(ratio-0.5)*0.18)
            candidates.append(TurnaroundCandidate(middle, score, balance, score*balance, ratio))
        candidates.sort(key=lambda item: item.final_score, reverse=True)
        if not candidates:
            raise InsufficientEvidenceError("No turnaround candidate was produced")
        return candidates[0], candidates[:10]


def turnaround_confidence(score: float, settings: DetectionSettings) -> str:
    if score >= settings.good_backtrack_score:
        return "high"
    if score >= settings.acceptable_backtrack_score:
        return "review"
    return "low"


def turnaround_to_dict(candidate: TurnaroundCandidate) -> dict:
    return asdict(candidate)
