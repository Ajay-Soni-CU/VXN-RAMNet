from __future__ import annotations
import numpy as np
from vxn_ramnet.core.exceptions import InsufficientEvidenceError


def l2_normalize_rows(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=np.float32)
    if matrix.ndim != 2:
        raise ValueError("Expected a two-dimensional embedding matrix")
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (matrix / norms).astype(np.float32)


def validate_embedding_pair(original: np.ndarray, flipped: np.ndarray, label: str) -> tuple[np.ndarray, np.ndarray]:
    original = np.asarray(original, dtype=np.float32)
    flipped = np.asarray(flipped, dtype=np.float32)
    if original.ndim != 2 or flipped.ndim != 2 or original.shape != flipped.shape:
        raise ValueError(f"Invalid original/flipped embedding pair for {label}: {original.shape} vs {flipped.shape}")
    if len(original) == 0:
        raise InsufficientEvidenceError(f"No embeddings available for {label}")
    if not np.all(np.isfinite(original)) or not np.all(np.isfinite(flipped)):
        raise ValueError(f"Non-finite embeddings for {label}")
    return original, flipped


def flip_aware_similarity(a: np.ndarray, af: np.ndarray, b: np.ndarray, bf: np.ndarray, chunk_size: int = 512) -> np.ndarray:
    a, af = validate_embedding_pair(a, af, "sequence-a")
    b, bf = validate_embedding_pair(b, bf, "sequence-b")
    if a.shape[1] != b.shape[1]:
        raise ValueError("Embedding dimensions do not match")
    output = np.empty((len(a), len(b)), dtype=np.float32)
    for start in range(0, len(a), chunk_size):
        stop = min(len(a), start + chunk_size)
        output[start:stop] = np.maximum.reduce([
            a[start:stop] @ b.T,
            af[start:stop] @ b.T,
            a[start:stop] @ bf.T,
            af[start:stop] @ bf.T,
        ])
    return output


def suppress_diagonal(matrix: np.ndarray, radius: int, fill_value: float = -1.0) -> np.ndarray:
    result = np.asarray(matrix, dtype=np.float32).copy()
    if result.ndim != 2 or result.shape[0] != result.shape[1]:
        raise ValueError("Diagonal suppression requires a square matrix")
    for index in range(len(result)):
        result[index, max(0, index-radius):min(len(result), index+radius+1)] = fill_value
    return result


def window_similarity_score(matrix: np.ndarray, first: int, second: int, radius: int) -> tuple[float, float, float]:
    same: list[float] = []
    reverse: list[float] = []
    for offset in range(-radius, radius + 1):
        i = first + offset
        j_same = second + offset
        j_reverse = second - offset
        if 0 <= i < matrix.shape[0] and 0 <= j_same < matrix.shape[1]:
            same.append(float(matrix[i, j_same]))
        if 0 <= i < matrix.shape[0] and 0 <= j_reverse < matrix.shape[1]:
            reverse.append(float(matrix[i, j_reverse]))
    same_score = float(np.mean(same)) if same else -1.0
    reverse_score = float(np.mean(reverse)) if reverse else -1.0
    return max(same_score, reverse_score), same_score, reverse_score


def normalized_centroid(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32)
    if values.ndim != 2 or len(values) == 0:
        raise InsufficientEvidenceError("Cannot calculate a centroid for an empty component")
    return l2_normalize_rows(np.mean(values, axis=0, keepdims=True))[0]
