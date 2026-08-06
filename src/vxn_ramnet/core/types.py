from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import numpy as np
from .enums import DecisionKind

FloatMatrix = np.ndarray

@dataclass(frozen=True)
class VideoMetadata:
    path: Path
    fps: float
    total_frames: int
    duration_seconds: float
    width: int
    height: int
    file_size_bytes: int

@dataclass(frozen=True)
class EncodedSequence:
    sequence_id: str
    embeddings: np.ndarray
    flipped_embeddings: np.ndarray
    frame_paths: tuple[str, ...]
    metadata: dict[str, Any]

@dataclass(frozen=True)
class BranchDecision:
    kind: DecisionKind
    branch_id: str | None
    confidence: float | None
    reason: str
    evidence: dict[str, Any]
