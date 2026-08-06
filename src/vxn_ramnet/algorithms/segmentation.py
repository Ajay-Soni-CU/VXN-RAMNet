from __future__ import annotations
from dataclasses import dataclass
from vxn_ramnet.config.models import DetectionSettings
from vxn_ramnet.core.exceptions import InsufficientEvidenceError

@dataclass(frozen=True)
class SegmentIndices:
    common: tuple[int, ...]
    junction: tuple[int, ...]
    branch_a: tuple[int, ...]
    backtrack: tuple[int, ...]
    branch_b: tuple[int, ...]

    def as_ranges(self) -> dict[str, list[list[int]]]:
        def ranges(values: tuple[int, ...]) -> list[list[int]]:
            groups: list[list[int]] = []
            for value in values:
                if not groups or value != groups[-1][1] + 1:
                    groups.append([value, value])
                else:
                    groups[-1][1] = value
            return groups
        return {
            "common_path": ranges(self.common),
            "junction": ranges(self.junction),
            "branch_a": ranges(self.branch_a),
            "backtrack": ranges(self.backtrack),
            "branch_b": ranges(self.branch_b),
        }


def _inclusive(start: int, end: int, n: int) -> tuple[int, ...]:
    start, end = max(0, start), min(n-1, end)
    return tuple(range(start, end+1)) if end >= start else ()


def build_segments(n: int, first: int, turnaround: int, returned: int, settings: DetectionSettings) -> SegmentIndices:
    if not (0 <= first < turnaround < returned < n):
        raise InsufficientEvidenceError(f"Invalid event ordering: first={first}, turnaround={turnaround}, return={returned}, n={n}")
    radius = settings.junction_memory_radius
    first_junction = _inclusive(first-radius, first+radius, n)
    return_junction = _inclusive(returned-radius, returned+radius, n)
    junction = tuple(sorted(set(first_junction+return_junction)))
    if settings.segment_policy == "legacy_overlap":
        common = _inclusive(0, first, n)
        branch_a = _inclusive(first+1, turnaround, n)
        backtrack = _inclusive(turnaround+1, returned, n)
        branch_b = _inclusive(returned+1, n-1, n)
    else:
        common = _inclusive(0, first-radius-1, n)
        branch_a = _inclusive(first+radius+1, turnaround, n)
        backtrack = _inclusive(turnaround+1, returned-radius-1, n)
        branch_b = _inclusive(returned+radius+1, n-1, n)
    named = {"common": common, "junction": junction, "branch_a": branch_a, "backtrack": backtrack, "branch_b": branch_b}
    empty = [name for name, values in named.items() if not values]
    if empty:
        raise InsufficientEvidenceError(f"Segmentation produced empty components {empty}; collect a longer journey or reduce junction radius")
    if settings.segment_policy == "disjoint":
        seen: set[int] = set()
        for name, values in named.items():
            overlap = seen.intersection(values)
            if overlap:
                raise RuntimeError(f"Disjoint segment policy violated in {name}: {sorted(overlap)[:5]}")
            seen.update(values)
    return SegmentIndices(common, junction, branch_a, backtrack, branch_b)
