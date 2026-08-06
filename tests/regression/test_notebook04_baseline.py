import json
from pathlib import Path

from vxn_ramnet.algorithms.junction import ConstrainedJunctionDetector
from vxn_ramnet.algorithms.segmentation import build_segments
from vxn_ramnet.algorithms.similarity import flip_aware_similarity, suppress_diagonal
from vxn_ramnet.algorithms.turnaround import ReverseSequenceTurnaroundDetector
from vxn_ramnet.config.models import PipelineConfig
from vxn_ramnet.core.enums import ComponentKind
from vxn_ramnet.core.types import EncodedSequence
from vxn_ramnet.io.npz import load_npz
from vxn_ramnet.memory.store import RouteMemoryStore
from vxn_ramnet.pipeline.runner import VxnPipeline

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "notebook04"


def test_verified_notebook04_embedding_baseline_is_preserved():
    expected = json.loads((FIXTURE / "expected.json").read_text(encoding="utf-8"))
    learning_data = load_npz(FIXTURE / "learning.npz", {"embeddings", "flipped_embeddings"})
    learning = EncodedSequence(
        "learning",
        learning_data["embeddings"],
        learning_data["flipped_embeddings"],
        tuple(str(i) for i in range(len(learning_data["embeddings"]))),
        {"encoder": {"encoder": "verified-notebook04-fixture"}},
    )
    config = PipelineConfig.model_validate({
        "learning_video": {"id": "learning", "path": "unused.mp4"},
        "query_videos": [
            {"id": "query_route_1", "path": "unused-1.mp4"},
            {"id": "query_route_2", "path": "unused-2.mp4"},
        ],
        "branch_a_name": "LEFT_BRANCH",
        "branch_b_name": "RIGHT_BRANCH",
        "detection": {"segment_policy": "legacy_overlap"},
        "decision": {"window_selection": "legacy_best"},
    })
    settings = config.detection
    similarity = flip_aware_similarity(
        learning.embeddings,
        learning.flipped_embeddings,
        learning.embeddings,
        learning.flipped_embeddings,
        settings.self_similarity_chunk_size,
    )
    similarity = suppress_diagonal(similarity, max(8, int(0.035 * len(learning.embeddings))))
    junction, _ = ConstrainedJunctionDetector(settings).detect(similarity)
    turnaround, _ = ReverseSequenceTurnaroundDetector(settings).detect(
        learning.embeddings,
        learning.flipped_embeddings,
        junction.first_index,
        junction.return_index,
    )
    assert junction.first_index == expected["first_junction_index"]
    assert junction.return_index == expected["return_junction_index"]
    assert turnaround.index == expected["turnaround_index"]

    segments = build_segments(
        len(learning.embeddings), junction.first_index, turnaround.index, junction.return_index, settings
    )
    segment_map = {
        ComponentKind.COMMON_PATH: segments.common,
        ComponentKind.JUNCTION: segments.junction,
        ComponentKind.BRANCH_A: segments.branch_a,
        ComponentKind.BACKTRACK: segments.backtrack,
        ComponentKind.BRANCH_B: segments.branch_b,
    }
    display_names = {
        ComponentKind.COMMON_PATH: "COMMON_PATH",
        ComponentKind.JUNCTION: "JUNCTION_A",
        ComponentKind.BRANCH_A: "LEFT_BRANCH",
        ComponentKind.BACKTRACK: "BACKTRACK_TO_JUNCTION",
        ComponentKind.BRANCH_B: "RIGHT_BRANCH",
    }
    memory = RouteMemoryStore.build(learning.embeddings, learning.flipped_embeddings, segment_map, display_names, {})
    pipeline = VxnPipeline(config)
    for query_id, expected_prediction in expected["predictions"].items():
        query_data = load_npz(FIXTURE / f"{query_id}.npz", {"embeddings", "flipped_embeddings"})
        query = EncodedSequence(
            query_id,
            query_data["embeddings"],
            query_data["flipped_embeddings"],
            tuple(str(i) for i in range(len(query_data["embeddings"]))),
            {},
        )
        result = pipeline._classify_query(query, memory)
        assert result["branch_id"] == expected_prediction
