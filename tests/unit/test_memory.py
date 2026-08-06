import numpy as np

from vxn_ramnet.algorithms.similarity import l2_normalize_rows
from vxn_ramnet.core.enums import ComponentKind
from vxn_ramnet.memory.store import RouteMemoryStore


def test_route_memory_round_trip(tmp_path):
    original = l2_normalize_rows(np.arange(100 * 8, dtype=np.float32).reshape(100, 8) + 1)
    flipped = original.copy()
    mapping = {
        ComponentKind.COMMON_PATH: tuple(range(0, 20)),
        ComponentKind.JUNCTION: tuple(range(20, 30)),
        ComponentKind.BRANCH_A: tuple(range(30, 50)),
        ComponentKind.BACKTRACK: tuple(range(50, 70)),
        ComponentKind.BRANCH_B: tuple(range(70, 100)),
    }
    names = {kind: kind.value.upper() for kind in mapping}
    memory = RouteMemoryStore.build(original, flipped, mapping, names, {
        "mode": "constrained_single_junction_backtracking",
        "topology_limit": "test constrained topology",
        "segment_policy": "disjoint",
        "events": {"first_junction_index": 20, "turnaround_index": 50, "return_junction_index": 70},
        "quality": {
            "junction_score": 0.8,
            "junction_confidence": "high",
            "backtrack_score": 0.7,
            "backtrack_confidence": "high",
        },
        "segments": {},
        "component_counts": {},
        "branch_label_note": "Exploration-order labels.",
        "encoder": {},
    })
    arrays = tmp_path / "memory.npz"
    metadata = tmp_path / "memory.json"
    RouteMemoryStore.save(memory, arrays, metadata)
    loaded = RouteMemoryStore.load(arrays, metadata)
    assert loaded.component(ComponentKind.BRANCH_A).embeddings.shape == (20, 8)
    assert loaded.metadata["artifact_schema_version"] == "1.0.0"
