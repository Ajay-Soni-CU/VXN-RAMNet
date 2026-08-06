from __future__ import annotations
from pathlib import Path
from typing import Mapping
import io
import numpy as np
from .atomic import atomic_write_bytes
from vxn_ramnet.core.exceptions import ArtifactError


def save_npz(path: str | Path, arrays: Mapping[str, np.ndarray]) -> Path:
    for key, value in arrays.items():
        arr = np.asarray(value)
        if arr.dtype == object:
            raise ArtifactError(f"Object arrays are forbidden in safe NPZ artifacts: {key}")
        if np.issubdtype(arr.dtype, np.floating) and not np.all(np.isfinite(arr)):
            raise ArtifactError(f"Non-finite values in array: {key}")
    buffer = io.BytesIO()
    np.savez_compressed(buffer, **arrays)
    return atomic_write_bytes(path, buffer.getvalue())


def load_npz(path: str | Path, required: set[str] | None = None) -> dict[str, np.ndarray]:
    source = Path(path)
    if not source.is_file():
        raise ArtifactError(f"NPZ artifact not found: {source}")
    try:
        with np.load(source, allow_pickle=False) as data:
            result = {key: data[key] for key in data.files}
    except Exception as exc:
        raise ArtifactError(f"Unsafe or corrupt NPZ artifact {source}: {exc}") from exc
    missing = (required or set()) - result.keys()
    if missing:
        raise ArtifactError(f"NPZ artifact {source} is missing keys: {sorted(missing)}")
    return result
