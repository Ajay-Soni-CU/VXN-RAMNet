from pathlib import Path

import cv2
import numpy as np

from vxn_ramnet.algorithms.similarity import l2_normalize_rows
from vxn_ramnet.config.models import PipelineConfig
from vxn_ramnet.pipeline.runner import VxnPipeline


class SyntheticRouteEncoder:
    def __init__(self, dimension: int = 64):
        rng = np.random.default_rng(7)
        self.common = l2_normalize_rows(rng.normal(size=(24, dimension)).astype(np.float32))
        self.junction = l2_normalize_rows(rng.normal(size=(7, dimension)).astype(np.float32))
        self.branch_a = l2_normalize_rows(rng.normal(size=(22, dimension)).astype(np.float32))
        self.branch_b = l2_normalize_rows(rng.normal(size=(20, dimension)).astype(np.float32))

    @property
    def manifest(self):
        return {"encoder": "synthetic-test", "embedding_dimension": self.common.shape[1]}

    def encode(self, frame_paths, *, flip=False):
        parent = Path(frame_paths[0]).parent.as_posix()
        n = len(frame_paths)
        if "/learning/" in parent:
            assert n == 100
            values = np.vstack([
                self.common[:22],
                self.junction,
                self.branch_a,
                self.branch_a[::-1],
                self.junction,
                self.branch_b,
            ])
            assert len(values) == 100
            return values.copy()
        common_count = 20
        if "query-a" in parent:
            route = self.branch_a
        else:
            route = self.branch_b
        route_indices = np.linspace(0, len(route) - 1, n - common_count, dtype=int)
        common_indices = np.linspace(2, 21, common_count, dtype=int)
        return np.vstack([self.common[common_indices], route[route_indices]]).astype(np.float32)


def make_video(path: Path, frames: int) -> None:
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (64, 48))
    assert writer.isOpened()
    for index in range(frames):
        frame = np.full((48, 64, 3), index % 255, dtype=np.uint8)
        writer.write(frame)
    writer.release()


def test_end_to_end_pipeline_with_injected_encoder(tmp_path):
    make_video(tmp_path / "learning.avi", 100)
    make_video(tmp_path / "query-a.avi", 60)
    make_video(tmp_path / "query-b.avi", 60)
    config = PipelineConfig.model_validate({
        "project_root": tmp_path,
        "learning_video": {"id": "learning-route", "path": "learning.avi"},
        "query_videos": [
            {"id": "query-a", "path": "query-a.avi"},
            {"id": "query-b", "path": "query-b.avi"},
        ],
        "frames": {
            "learning_count": 100,
            "query_count": 60,
            "learning_max_seconds": 20,
            "query_max_seconds": 10,
            "allowed_extensions": [".avi"],
        },
        "detection": {
            "first_junction_search": [0.15, 0.40],
            "return_junction_search": [0.60, 0.85],
            "expected_first_junction_ratio": 0.25,
            "expected_return_junction_ratio": 0.75,
            "junction_window": 2,
            "junction_memory_radius": 2,
            "min_junction_gap_ratio": 0.30,
            "segment_policy": "disjoint",
        },
        "decision": {"window_selection": "top_k_mean", "top_k_windows": 3},
        "artifacts": {"output_root": "runs", "run_id": "run-test", "save_frames": False},
    })
    result = VxnPipeline(config, SyntheticRouteEncoder()).run()
    decisions = {row["query_id"]: row for row in result.summary["query_results"]}
    assert decisions["query-a"]["branch_id"] == "BRANCH_A"
    assert decisions["query-b"]["branch_id"] == "BRANCH_B"
    assert result.summary["route_memory"]["segment_policy"] == "disjoint"
    assert (result.run_directory / "manifest.json").is_file()
    assert not (result.run_directory / "frames").exists()
