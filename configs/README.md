# Configurations

`camera_baseline.yaml` is the tracked reference configuration for the current constrained camera experiment.

Create an untracked local copy and edit its input paths:

```bash
cp configs/camera_baseline.yaml configs/local.yaml
```

Configuration rules:

- Learning and query IDs must be unique safe identifiers.
- Branch A/B are exploration-order labels.
- Unknown fields are rejected.
- Input videos are validated before managed output directories are created or replaced.
- Research parameter changes should be recorded in an experiment protocol rather than silently replacing the baseline file.
