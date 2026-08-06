from __future__ import annotations
import re
import shutil
from pathlib import Path
from vxn_ramnet.core.exceptions import ConfigurationError

_ID = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")

def validate_identifier(value: str) -> str:
    if not _ID.fullmatch(value):
        raise ConfigurationError(f"Unsafe identifier: {value!r}")
    return value


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def prepare_run_directory(output_root: Path, run_id: str, overwrite: bool) -> Path:
    validate_identifier(run_id)
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    run_dir = (output_root / run_id).resolve()
    if not is_within(run_dir, output_root) or run_dir == output_root:
        raise ConfigurationError("Resolved run directory escapes output_root")
    if run_dir.exists():
        if not overwrite:
            raise FileExistsError(f"Run already exists: {run_dir}")
        marker = run_dir / ".vxn-run"
        if not marker.is_file():
            raise ConfigurationError(f"Refusing to delete unmarked directory: {run_dir}")
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    (run_dir / ".vxn-run").write_text("VXN-RAMNet managed run directory\n", encoding="utf-8")
    return run_dir


def remove_managed_subdirectory(path: Path, run_root: Path) -> None:
    """Delete a generated subdirectory only inside a marked VXN run."""
    path = path.resolve()
    run_root = run_root.resolve()
    if not (run_root / ".vxn-run").is_file():
        raise ConfigurationError(f"Refusing cleanup in an unmarked run: {run_root}")
    if path == run_root or not is_within(path, run_root):
        raise ConfigurationError(f"Refusing unsafe managed-subdirectory cleanup: {path}")
    if path.exists():
        shutil.rmtree(path)
