from __future__ import annotations
import numpy as np
from .similarity import flip_aware_similarity


def component_score(query: np.ndarray, query_flip: np.ndarray, memory: np.ndarray, memory_flip: np.ndarray, centroid: np.ndarray, chunk_size: int = 512) -> tuple[float, np.ndarray]:
    if len(query) == 0 or len(memory) == 0:
        return 0.0, np.empty((0,), dtype=np.float32)
    similarity = flip_aware_similarity(query, query_flip, memory, memory_flip, chunk_size)
    best = np.max(similarity, axis=1)
    top_count = min(3, similarity.shape[1])
    top = np.partition(similarity, similarity.shape[1]-top_count, axis=1)[:, -top_count:]
    top_mean = np.mean(top, axis=1)
    c = np.asarray(centroid, dtype=np.float32).reshape(1, -1)
    centroid_score = np.maximum((query@c.T).ravel(), (query_flip@c.T).ravel())
    per_frame = 0.50*best + 0.30*top_mean + 0.20*centroid_score
    return float(np.mean(per_frame)), per_frame.astype(np.float32)


def branch_windows(n: int) -> list[tuple[int, int]]:
    if n < 20:
        return []
    starts = sorted({int(r*n) for r in (0.45,0.50,0.55,0.60,0.65,0.70,0.75)})
    windows: set[tuple[int,int]] = set()
    for start in starts:
        for ratio in (0.20,0.25,0.30,0.35):
            end = min(n, start+max(12,int(ratio*n)))
            if end-start >= 10:
                windows.add((start,end))
    for ratio in (0.60,0.65,0.70):
        start=int(ratio*n)
        if n-start>=10: windows.add((start,n))
    return sorted(windows)


def interval_iou(a: tuple[int,int], b: tuple[int,int]) -> float:
    inter=max(0,min(a[1],b[1])-max(a[0],b[0]))
    union=max(a[1],b[1])-min(a[0],b[0])
    return inter/union if union else 0.0


def select_diverse_top_windows(rows: list[dict], k: int) -> list[dict]:
    selected: list[dict] = []
    for row in sorted(rows,key=lambda x:x["window_quality"],reverse=True):
        interval=(row["start"],row["end"])
        if all(interval_iou(interval,(other["start"],other["end"]))<0.70 for other in selected):
            selected.append(row)
            if len(selected)>=k: break
    if not selected and rows: selected=[max(rows,key=lambda x:x["window_quality"])]
    return selected
