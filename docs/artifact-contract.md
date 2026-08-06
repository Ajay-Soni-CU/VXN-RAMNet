# Artifact contract

## Run isolation

Every execution writes to one managed directory:

```text
artifacts/runs/<run-id>/
```

The runtime creates a `.vxn-run` marker and refuses to delete an existing directory that does not contain that marker. Inputs are validated before the managed run is created or overwritten.

## Current layout

```text
<run-id>/
├── .vxn-run
├── config.snapshot.json
├── manifest.json
├── inputs/
│   └── preflight.json
├── frames/
├── embeddings/
│   ├── learning/
│   └── queries/
├── memory/
│   ├── route-memory.npz
│   ├── route-memory.json
│   └── self-similarity.npz       # optional
├── reports/
│   ├── queries/
│   ├── query-decisions.json
│   ├── query-results.csv
│   ├── report.md
│   └── summary.json
├── logs/
│   └── pipeline.jsonl
└── stages/
```

## Safety rules

- NPZ files are loaded with `allow_pickle=False`.
- Object arrays are rejected.
- Non-finite floating arrays are rejected when writing safe NPZ artifacts.
- JSON, text, and NPZ writes use temporary files and atomic replacement.
- User-provided identifiers are restricted before becoming paths or filenames.
- CSV cells are neutralized when they could be interpreted as spreadsheet formulas.
- Markdown fields are escaped before report generation.

## Versioning

The package version and artifact schema version are separate:

- Package version describes code evolution.
- Artifact schema version changes only when persisted structures change incompatibly.

The current artifact schema is `1.0.0`. Before changing it:

1. Document the field-level change.
2. Add migration or explicit rejection behavior.
3. Add tests for old and new artifacts.
4. Update the relevant JSON schema.
5. Record the change in `CHANGELOG.md`.

## Route-memory semantics

The current memory represents a constrained segmented journey, not a general graph database. Components are:

- `common_path`
- `junction`
- `branch_a`
- `backtrack`
- `branch_b`

Branch labels are exploration-order labels. Metadata must preserve detector settings, event indices, component ranges, quality scores, encoder information, and the topology limitation.

## Data policy

Do not commit raw videos, extracted frames, participant data, private route data, model weights, or generated run directories. The `.gitignore` blocks common forms, but researchers remain responsible for reviewing commits.
