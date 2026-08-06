from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from vxn_ramnet.core.exceptions import ArtifactError


def validate_schema(schema_name: str, payload: Any) -> None:
    """Validate a payload against a packaged JSON schema."""
    schema_root = files("vxn_ramnet.schemas")
    try:
        schemas = {
            resource.name: json.loads(resource.read_text(encoding="utf-8"))
            for resource in schema_root.iterdir()
            if resource.name.endswith(".json")
        }
        schema = schemas[schema_name]
        registry = Registry().with_resources(
            (
                document.get("$id", name),
                Resource.from_contents(document),
            )
            for name, document in schemas.items()
        )
        errors = sorted(
            Draft202012Validator(schema, registry=registry).iter_errors(payload),
            key=lambda error: list(error.path),
        )
    except Exception as exc:
        if isinstance(exc, ArtifactError):
            raise
        raise ArtifactError(f"Could not validate schema {schema_name}: {exc}") from exc
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path) or "<root>"
        raise ArtifactError(f"Schema validation failed at {location}: {first.message}")
