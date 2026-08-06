from __future__ import annotations
from pathlib import Path
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Identifier = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{1,63}$")]

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

class VideoInput(StrictModel):
    id: Identifier
    path: Path

class FrameSettings(StrictModel):
    learning_count: int = Field(default=270, ge=40, le=2000)
    query_count: int = Field(default=120, ge=20, le=1000)
    learning_max_seconds: float = Field(default=45.0, gt=0, le=600)
    query_max_seconds: float = Field(default=20.0, gt=0, le=300)
    jpeg_quality: int = Field(default=92, ge=60, le=100)
    minimum_saved_ratio: float = Field(default=0.90, ge=0.5, le=1.0)
    maximum_input_bytes: int = Field(default=750_000_000, ge=1_000_000)
    allowed_extensions: tuple[str, ...] = (".mp4", ".mov", ".avi", ".mkv", ".webm")

    @field_validator("allowed_extensions")
    @classmethod
    def normalize_extensions(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(sorted({e.lower() if e.startswith(".") else f".{e.lower()}" for e in value}))
        if not normalized:
            raise ValueError("At least one video extension must be allowed")
        return normalized

class EncoderSettings(StrictModel):
    name: Literal["efficientnet_b0"] = "efficientnet_b0"
    input_size: tuple[int, int] = (224, 224)
    batch_size: int = Field(default=16, ge=1, le=256)
    weights: str = "imagenet"
    weights_path: Path | None = None
    allow_remote_weight_resolution: bool = True
    dtype: Literal["float32"] = "float32"

    @field_validator("input_size")
    @classmethod
    def validate_input_size(cls, value: tuple[int, int]) -> tuple[int, int]:
        if len(value) != 2 or any(v < 32 or v > 1024 for v in value):
            raise ValueError("input_size must contain two values between 32 and 1024")
        return value

    @model_validator(mode="after")
    def validate_weights(self) -> "EncoderSettings":
        if self.weights_path is not None and self.weights != "local":
            raise ValueError("Set weights='local' when weights_path is provided")
        if self.weights == "local" and self.weights_path is None:
            raise ValueError("weights_path is required when weights='local'")
        return self

class DetectionSettings(StrictModel):
    first_junction_search: tuple[float, float] = (0.12, 0.48)
    return_junction_search: tuple[float, float] = (0.48, 0.86)
    junction_window: int = Field(default=5, ge=1, le=30)
    junction_memory_radius: int = Field(default=6, ge=1, le=50)
    min_junction_gap_ratio: float = Field(default=0.18, gt=0, lt=0.8)
    expected_first_junction_ratio: float = Field(default=0.35, ge=0, le=1)
    expected_return_junction_ratio: float = Field(default=0.68, ge=0, le=1)
    plausibility_weight: float = Field(default=0.20, ge=0, le=1)
    good_junction_score: float = Field(default=0.70, ge=-1, le=1)
    acceptable_junction_score: float = Field(default=0.56, ge=-1, le=1)
    good_backtrack_score: float = Field(default=0.56, ge=-1, le=1)
    acceptable_backtrack_score: float = Field(default=0.42, ge=-1, le=1)
    reverse_sample_count: int = Field(default=28, ge=8, le=256)
    self_similarity_chunk_size: int = Field(default=512, ge=32, le=4096)
    segment_policy: Literal["disjoint", "legacy_overlap"] = "disjoint"

    @model_validator(mode="after")
    def validate_ranges(self) -> "DetectionSettings":
        for name, pair in (("first_junction_search", self.first_junction_search), ("return_junction_search", self.return_junction_search)):
            if len(pair) != 2 or not 0 <= pair[0] < pair[1] <= 1:
                raise ValueError(f"{name} must be an increasing ratio pair inside [0, 1]")
        if self.first_junction_search[0] >= self.return_junction_search[1]:
            raise ValueError("Junction search ranges do not permit an ordered pair")
        if self.acceptable_junction_score > self.good_junction_score:
            raise ValueError("acceptable_junction_score cannot exceed good_junction_score")
        if self.acceptable_backtrack_score > self.good_backtrack_score:
            raise ValueError("acceptable_backtrack_score cannot exceed good_backtrack_score")
        return self

class DecisionSettings(StrictModel):
    minimum_branch_score: float = Field(default=0.58, ge=-1, le=1)
    minimum_branch_gap: float = Field(default=0.04, ge=0, le=2)
    strong_branch_score: float = Field(default=0.72, ge=-1, le=1)
    strong_branch_gap: float = Field(default=0.07, ge=0, le=2)
    unknown_score: float = Field(default=0.54, ge=-1, le=1)
    window_selection: Literal["top_k_mean", "legacy_best"] = "top_k_mean"
    top_k_windows: int = Field(default=3, ge=1, le=20)
    confidence_temperature: float = Field(default=0.08, gt=0, le=1)

    @model_validator(mode="after")
    def validate_thresholds(self) -> "DecisionSettings":
        if self.strong_branch_score < self.minimum_branch_score:
            raise ValueError("strong_branch_score must be >= minimum_branch_score")
        if self.strong_branch_gap < self.minimum_branch_gap:
            raise ValueError("strong_branch_gap must be >= minimum_branch_gap")
        return self

class ArtifactSettings(StrictModel):
    output_root: Path = Path("artifacts/runs")
    run_id: Identifier | None = None
    overwrite_existing_run: bool = False
    resume: bool = False
    save_frames: bool = True
    save_self_similarity_matrix: bool = False

class RuntimeSettings(StrictModel):
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    deterministic_seed: int = 42
    fail_on_degraded_graph: bool = False
    include_diagnostic_details: bool = False

class PipelineConfig(StrictModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    project_root: Path = Path(".")
    learning_video: VideoInput
    query_videos: list[VideoInput] = Field(min_length=1)
    branch_a_name: str = Field(default="BRANCH_A", min_length=1, max_length=64)
    branch_b_name: str = Field(default="BRANCH_B", min_length=1, max_length=64)
    frames: FrameSettings = Field(default_factory=FrameSettings)
    encoder: EncoderSettings = Field(default_factory=EncoderSettings)
    detection: DetectionSettings = Field(default_factory=DetectionSettings)
    decision: DecisionSettings = Field(default_factory=DecisionSettings)
    artifacts: ArtifactSettings = Field(default_factory=ArtifactSettings)
    runtime: RuntimeSettings = Field(default_factory=RuntimeSettings)

    @model_validator(mode="after")
    def validate_pipeline(self) -> "PipelineConfig":
        ids = [self.learning_video.id, *(v.id for v in self.query_videos)]
        if len(ids) != len(set(ids)):
            raise ValueError("Learning and query video IDs must be unique")
        if self.branch_a_name.strip() == self.branch_b_name.strip():
            raise ValueError("Branch names must be distinct")
        if not self.branch_a_name.strip() or not self.branch_b_name.strip():
            raise ValueError("Branch names cannot be blank")
        output = self.resolved_output_root
        project = self.project_root.resolve()
        if output == project:
            raise ValueError("output_root cannot be the project root")
        return self

    def resolve_input(self, item: VideoInput) -> Path:
        return item.path.resolve() if item.path.is_absolute() else (self.project_root / item.path).resolve()

    @property
    def resolved_output_root(self) -> Path:
        return self.artifacts.output_root.resolve() if self.artifacts.output_root.is_absolute() else (self.project_root / self.artifacts.output_root).resolve()
