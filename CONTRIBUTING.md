# Contributing

## Scope discipline

- Keep implemented camera-baseline capabilities separate from proposed VisionX features.
- Do not add placeholder modules solely to make the repository appear complete.
- Add a module only when it owns a real, independently testable responsibility.
- Do not make production, safety, medical, or accuracy claims without evidence.

## Development workflow

```bash
pip install -e ".[dev]"
ruff check src tests scripts apps
mypy src/vxn_ramnet
pytest
```

For behavior changes:

1. State the research or engineering reason.
2. Add or update tests.
3. Update configuration and artifact documentation when applicable.
4. Record scientific changes in an experiment protocol.
5. Preserve backward compatibility or document the migration.

## Definition of done

A change is complete when:

- Public behavior and limitations are documented.
- Invalid inputs and failure paths are tested.
- Persisted-format changes include schema/version handling.
- No raw videos, participant data, secrets, generated artifacts, or model weights are committed.
- Research conclusions identify the dataset, split, metrics, and limitations.
