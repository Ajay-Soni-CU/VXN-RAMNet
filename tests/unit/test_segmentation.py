from vxn_ramnet.algorithms.segmentation import build_segments
from vxn_ramnet.config.models import DetectionSettings


def test_disjoint_segmentation_has_no_shared_indices():
    segments = build_segments(100, 25, 50, 75, DetectionSettings(junction_memory_radius=3, segment_policy="disjoint"))
    groups = [segments.common, segments.junction, segments.branch_a, segments.backtrack, segments.branch_b]
    flattened = [value for group in groups for value in group]
    assert len(flattened) == len(set(flattened))


def test_legacy_overlap_is_explicit():
    segments = build_segments(100, 25, 50, 75, DetectionSettings(junction_memory_radius=3, segment_policy="legacy_overlap"))
    assert 25 in segments.common
    assert 25 in segments.junction
