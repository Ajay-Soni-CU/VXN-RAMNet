from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import yaml
from .models import PipelineConfig
from vxn_ramnet.core.exceptions import ConfigurationError


def load_config(path: str | Path) -> PipelineConfig:
    source = Path(path)
    if not source.is_file():
        raise ConfigurationError(f"Configuration file does not exist: {source}")
    try:
        text = source.read_text(encoding="utf-8")
        if source.suffix.lower() in {".yaml", ".yml"}:
            payload: Any = yaml.safe_load(text)
        elif source.suffix.lower() == ".json":
            payload = json.loads(text)
        else:
            raise ConfigurationError("Configuration must be JSON or YAML")
        if not isinstance(payload, dict):
            raise ConfigurationError("Configuration root must be an object")
        return PipelineConfig.model_validate(payload)
    except ConfigurationError:
        raise
    except Exception as exc:
        raise ConfigurationError(f"Invalid configuration {source}: {exc}") from exc


def dump_config(config: PipelineConfig, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = config.model_dump(mode="json")
    if target.suffix.lower() in {".yaml", ".yml"}:
        target.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    elif target.suffix.lower() == ".json":
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    else:
        raise ConfigurationError("Configuration output must be JSON or YAML")
