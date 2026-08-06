from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import traceback

from vxn_ramnet.core.enums import StageStatus
from vxn_ramnet.io.atomic import atomic_write_json
from vxn_ramnet.io.paths import prepare_run_directory, validate_identifier


@dataclass(frozen=True)
class RunLayout:
    root: Path

    @property
    def config(self) -> Path:
        return self.root / "config.snapshot.json"

    @property
    def manifest(self) -> Path:
        return self.root / "manifest.json"

    @property
    def preflight(self) -> Path:
        return self.root / "inputs" / "preflight.json"

    @property
    def frames(self) -> Path:
        return self.root / "frames"

    @property
    def frame_report(self) -> Path:
        return self.root / "frames" / "frame-extraction.json"

    @property
    def embeddings(self) -> Path:
        return self.root / "embeddings"

    @property
    def memory_arrays(self) -> Path:
        return self.root / "memory" / "route-memory.npz"

    @property
    def memory_metadata(self) -> Path:
        return self.root / "memory" / "route-memory.json"

    @property
    def reports(self) -> Path:
        return self.root / "reports"

    @property
    def logs(self) -> Path:
        return self.root / "logs" / "pipeline.jsonl"

    @property
    def stages(self) -> Path:
        return self.root / "stages"


class ArtifactStore:
    def __init__(self, layout: RunLayout, include_diagnostic_details: bool = False):
        self.layout = layout
        self.include_diagnostic_details = include_diagnostic_details

    @classmethod
    def create(
        cls,
        output_root: Path,
        run_id: str,
        overwrite: bool,
        resume: bool = False,
        include_diagnostic_details: bool = False,
    ) -> "ArtifactStore":
        validate_identifier(run_id)
        candidate = (output_root / run_id).resolve()
        if resume:
            if not (candidate / ".vxn-run").is_file():
                raise FileNotFoundError(f"Cannot resume unmanaged or missing run: {candidate}")
            return cls(RunLayout(candidate), include_diagnostic_details)
        return cls(
            RunLayout(prepare_run_directory(output_root, run_id, overwrite)),
            include_diagnostic_details,
        )

    def stage_state_path(self, name: str) -> Path:
        return self.layout.stages / f"{name}.json"

    def is_complete(self, name: str, outputs: list[Path]) -> bool:
        import json

        state = self.stage_state_path(name)
        if not state.is_file() or not all(path.exists() for path in outputs):
            return False
        try:
            return json.loads(state.read_text(encoding="utf-8")).get("status") == StageStatus.SUCCEEDED
        except Exception:
            return False

    @contextmanager
    def stage(self, name: str):
        started = datetime.now(timezone.utc)
        atomic_write_json(
            self.stage_state_path(name),
            {
                "stage": name,
                "status": StageStatus.RUNNING,
                "started_at": started.isoformat(),
            },
        )
        try:
            yield
        except Exception as exc:
            payload = {
                "stage": name,
                "status": StageStatus.FAILED,
                "started_at": started.isoformat(),
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "error_type": type(exc).__name__,
                "error": "Diagnostic details are redacted by default.",
            }
            if self.include_diagnostic_details:
                payload["error"] = str(exc)
                payload["traceback"] = traceback.format_exc()
            atomic_write_json(self.stage_state_path(name), payload)
            raise
        else:
            atomic_write_json(
                self.stage_state_path(name),
                {
                    "stage": name,
                    "status": StageStatus.SUCCEEDED,
                    "started_at": started.isoformat(),
                    "finished_at": datetime.now(timezone.utc).isoformat(),
                },
            )
