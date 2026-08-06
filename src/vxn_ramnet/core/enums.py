from enum import StrEnum

class DecisionKind(StrEnum):
    KNOWN_BRANCH = "known_branch"
    UNCERTAIN = "uncertain"
    UNKNOWN_ROUTE = "unknown_route"

class StageStatus(StrEnum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"

class ComponentKind(StrEnum):
    COMMON_PATH = "common_path"
    JUNCTION = "junction"
    BRANCH_A = "branch_a"
    BACKTRACK = "backtrack"
    BRANCH_B = "branch_b"
