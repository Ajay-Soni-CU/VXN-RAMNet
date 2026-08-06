# Project status

Last reviewed: 2026-08-05

## Status vocabulary

- **Implemented:** executable and covered by repository tests.
- **Partial:** some engineering exists, but the scientific or operational requirement is incomplete.
- **Not implemented:** documented target only.

## Current camera baseline

| Capability | Status | Evidence | Remaining work |
|---|---|---|---|
| Configuration validation | Implemented | Pydantic models and unit tests | Add experiment-specific presets after calibration |
| Video preflight | Implemented | Extension, size, decode, metadata, and frame-write checks | Add corrupted-stream corpus and codec compatibility matrix |
| Frame sampling | Implemented | Deterministic unique indices and integration tests | Compare uniform, motion-aware, and quality-aware sampling |
| EfficientNetB0 encoder | Implemented | Adapter for frozen ImageNet embeddings | Pin and record approved weight checksum; benchmark alternatives |
| Flip-aware similarity | Implemented | Numerical unit tests | Measure whether flipping helps or harms across environments |
| Junction revisit detection | Implemented for constrained topology | Notebook 4 regression fixture | Evaluate on held-out routes and remove fixed temporal dependence |
| Turnaround detection | Implemented for constrained topology | Notebook 4 regression fixture | Evaluate against IMU/annotation ground truth |
| Route-memory segmentation | Implemented | Unit tests for disjoint and legacy policies | Quantify boundary sensitivity and component leakage |
| Branch classification | Implemented | Multi-window scoring and regression test | Calibrate thresholds and confidence on held-out data |
| Unknown/uncertain decisions | Partial | Rule-based abstention exists | Build unknown-route benchmark and reliability analysis |
| Reports and artifacts | Implemented | JSON, CSV, Markdown, NPZ, stage state, manifest | Freeze public schema only after repeated experiments |
| Reproducible evaluation | Partial | Tests and config snapshots exist | Add dataset versioning, split manifest, seeds, metrics, and result tables |
| Runtime performance | Partial | Batch processing works | Add CPU/mobile benchmarks, memory profile, and bounded latency targets |

## VisionX target system

| Capability | Status | Required proof before claiming completion |
|---|---|---|
| Raspberry Pi Zero 2 W sensor node | Not implemented | Timestamped camera/IMU/distance packets under measured load |
| Shared time base and packet protocol | Not implemented | Loss, reorder, duplicate, stale-data, and clock-drift tests |
| IMU calibration and conditioning | Not implemented | Bias, gravity, filter, drift, and repeatability evaluation |
| Turn and turnaround events | Not implemented | Annotated motion dataset with precision/recall and rejection tests |
| Visual-inertial fusion | Not implemented | Held-out ablation proving fusion improves reliability |
| Android streaming runtime | Not implemented | On-device latency, memory, thermal, and battery measurements |
| Ultrasonic supervisory warning | Not implemented | Controlled obstacle tests and failure-mode analysis |
| Guidance state machine | Not implemented | Deterministic state-transition and fail-safe tests |
| TTS and bone-conduction output | Not implemented | Accessibility and usability testing with appropriate supervision |
| Assistive field validation | Not implemented | Ethics, consent, risk controls, representative testing, and independent review |

## Definition of the next credible research release

The next release is not complete merely because the code runs. It should require:

1. A documented dataset and collection protocol.
2. Route-level and participant-level train/calibration/test separation.
3. Baseline comparisons and ablation studies.
4. Threshold calibration using only calibration data.
5. Known, uncertain, and unknown-route metrics.
6. Reproducible experiment manifests and retained result tables.
7. CPU runtime and memory measurements.
8. A limitations section that matches the evidence.

Until these conditions are met, the project remains an engineered experimental baseline rather than a validated route-recognition system.
