# Current camera-baseline architecture

## Scope and topology

The executable package implements one offline learning journey with the constrained topology:

```text
common path → first junction visit → Branch A → turnaround
            → return junction visit → Branch B
```

This is a segmented route-memory experiment, not a general graph-navigation engine. Branch A and Branch B are assigned by exploration order. The current camera pipeline cannot prove physical left/right direction.

## Entry points

| Entry point | Purpose |
|---|---|
| `vxn-ramnet` | Installed command-line interface |
| `scripts/run_pipeline.py` | Source-checkout convenience wrapper |
| `apps/streamlit_app.py` | Optional isolated local demonstration UI |
| `VxnPipeline` | Programmatic orchestration API |

## Pipeline stages

### 1. Configuration and preflight

`PipelineConfig` rejects unknown fields and validates identifiers, paths, frame counts, search ranges, thresholds, encoder settings, branch labels, and output placement.

Before a managed run is created, the pipeline checks every learning/query video for:

- Existence and supported extension.
- Non-zero size and configured size limit.
- OpenCV decode capability.
- Frame count, dimensions, frame rate, and duration.
- Duplicate sequence identifiers.

This ordering prevents the original failure mode in which outputs could be deleted before all inputs were known to be valid.

### 2. Frame extraction

Frames are sampled deterministically across a bounded duration. Sampling indices are unique, and each image write is checked. The saved-frame ratio must pass the configured quality threshold.

The current strategy is uniform temporal sampling. Motion-aware and image-quality-aware sampling remain research tasks.

### 3. Visual encoding

For every sampled frame, the encoder produces:

- An embedding for the original image.
- An embedding for the horizontally flipped image.

The default adapter uses frozen ImageNet EfficientNetB0 and L2-normalizes embeddings. The encoder interface is injectable so tests and future model comparisons do not depend on TensorFlow execution.

### 4. Flip-aware self-similarity

For sequence positions `i` and `j`, the similarity stage evaluates original/original, flipped/original, original/flipped, and flipped/flipped cosine similarities and keeps the maximum. Near-diagonal similarity is suppressed so the detector searches for revisits rather than trivial adjacent-frame similarity.

This operation is quadratic in the number of learning frames and is a known scaling limitation.

### 5. Junction-revisit detection

The constrained detector searches configured early and later temporal regions for the most plausible similar sequence windows. Its score combines visual window similarity with a small temporal plausibility prior.

The detector assumes that the first junction and return junction fall inside broad configured regions. That assumption must be evaluated on routes with different journey timing.

### 6. Turnaround detection

Between the detected junction visits, the algorithm compares forward sequence evidence with reverse sequence evidence to estimate the transition from outward travel to backtracking.

The output is an estimated turnaround index and a raw backtrack-consistency score. The current quality labels are threshold-based engineering categories, not calibrated confidence probabilities.

### 7. Route-memory segmentation

The learning sequence is divided into:

- `common_path`
- `junction`
- `branch_a`
- `backtrack`
- `branch_b`

The default policy uses disjoint ranges to reduce shared-frame leakage. A legacy-overlap option exists only for regression compatibility.

For each component, the memory stores original embeddings, flipped embeddings, a normalized centroid, labels, ranges, event indices, detector quality values, and encoder metadata.

### 8. Query classification

Later windows from a query journey are compared with common-path, junction, Branch A, and Branch B memory components.

The component score combines:

- Best frame-to-memory similarity.
- Mean of the strongest matches.
- Query-to-component-centroid similarity.

Window quality rewards branch evidence and branch separation while penalizing strong common/junction evidence. The current default aggregates several diverse high-quality windows instead of accepting a single optimistic best window.

The decision layer can return:

- Known Branch A.
- Known Branch B.
- Uncertain—insufficient separation or evidence.
- Unknown route—scores below the configured acceptance region.

### 9. Artifacts and reports

Each run creates a versioned route-memory artifact, per-query result files, final JSON/CSV/Markdown reports, a configuration snapshot, input manifest, logs, and stage-state files. See [Artifact contract](../artifact-contract.md).

## Source-module responsibilities

| Package | Responsibility |
|---|---|
| `algorithms` | Pure numerical detection, segmentation, scoring, similarity, and decisions |
| `config` | Strict configuration models and YAML/JSON loading |
| `core` | Shared enums, typed records, exceptions, and versions |
| `io` | Video validation, safe paths, atomic persistence, checksums, NPZ and schema handling |
| `memory` | Route-memory construction, schema, loading, and saving |
| `observability` | Local structured logging and run manifest creation |
| `pipeline` | Stage orchestration, run layout, resumption state, and serialization |
| `reporting` | Sanitized JSON, CSV, and Markdown reporting |
| `vision` | Preprocessing and visual-encoder abstraction/adapters |

## What the regression test proves

The regression fixture reproduces the bundled Notebook 4 baseline:

- First junction index: 60.
- Turnaround index: 134.
- Return junction index: 193.
- The two sample query decisions in legacy-compatible mode.

This proves that the modular implementation preserves the known sample behavior. It does not prove accuracy on new routes, users, cameras, or environments.

## Remaining scientific limitations

- One-junction/two-branch topology.
- Quadratic self-similarity.
- Heuristic temporal priors.
- Hand-tuned, uncalibrated thresholds.
- Post-hoc full-video analysis rather than incremental streaming.
- No representative known/unknown benchmark.
- No independent user or accessibility validation.
- No validated physical turn direction.
- The stored backtrack component is not yet directly used by the query classifier.
