from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def atomic_write_bytes(path: str | Path, data: bytes) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, target)
        return target
    finally:
        tmp.unlink(missing_ok=True)


def atomic_write_text(path: str | Path, text: str) -> Path:
    return atomic_write_bytes(path, text.encode("utf-8"))


def atomic_write_json(path: str | Path, payload: Any) -> Path:
    return atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=False, ensure_ascii=False) + "\n")
