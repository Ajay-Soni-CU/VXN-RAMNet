from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np
from vxn_ramnet.core.enums import ComponentKind

COMPONENT_ORDER = (
    ComponentKind.COMMON_PATH,
    ComponentKind.JUNCTION,
    ComponentKind.BRANCH_A,
    ComponentKind.BACKTRACK,
    ComponentKind.BRANCH_B,
)

@dataclass(frozen=True)
class ComponentMemory:
    kind: ComponentKind
    display_name: str
    embeddings: np.ndarray
    flipped_embeddings: np.ndarray
    centroid: np.ndarray
    source_indices: np.ndarray

@dataclass(frozen=True)
class RouteMemory:
    components: dict[ComponentKind, ComponentMemory]
    metadata: dict[str, Any]

    def component(self, kind: ComponentKind) -> ComponentMemory:
        return self.components[kind]
