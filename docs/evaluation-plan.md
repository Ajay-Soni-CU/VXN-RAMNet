# Evaluation plan

## Purpose

The current repository proves that a constrained algorithm can reproduce the bundled Notebook 4 sample. It does not establish accuracy, generalization, safety, or usefulness. This plan defines the minimum evidence needed for credible research claims.

## Evaluation units

Use route-level and session-level units rather than treating individual frames as independent samples. Frame-level random splits would leak nearly identical observations across train and test sets.

Recommended hierarchy:

- Participant
- Physical route
- Route topology
- Collection session
- Journey video
- Timestamped frame or sensor packet

## Required splits

1. **Development set:** algorithm design and debugging.
2. **Calibration set:** threshold selection, confidence mapping, and stopping rules.
3. **Final test set:** frozen, held-out evaluation.

Where participant data is collected, include participant-disjoint reporting. Where the same physical route appears in multiple sets, explicitly label the experiment as repeat-route recognition rather than unseen-route generalization.

## Scenario coverage

The dataset should include:

- Repeated known branches.
- Unknown routes.
- Visually similar corridors or roads.
- Different lighting and weather.
- Camera yaw/pitch variation.
- Slow, normal, and fast walking.
- Partial journeys and early stopping.
- Reverse traversal.
- Occlusion and motion blur.
- Junctions at different relative positions in the sequence.
- Sensor degradation for future multimodal tests.

## Metrics

### Event detection

- First-junction index/time error.
- Turnaround index/time error.
- Return-junction index/time error.
- Detection success rate within predefined temporal tolerances.

### Branch recognition

- Accuracy and macro F1 on known branches.
- Confusion matrix.
- Per-route and per-participant results.
- Coverage: fraction of journeys receiving a known decision.
- Selective risk: error rate among non-abstained decisions.

### Unknown and uncertainty handling

- Unknown-route AUROC and AUPRC.
- False-known rate: unknown journeys incorrectly accepted as a known branch.
- False-branch rate.
- Abstention rate.
- Coverage-risk and threshold curves.

### Confidence quality

- Reliability diagram.
- Expected calibration error where appropriate.
- Brier score for probabilistic outputs only after a calibrated probability model exists.

Current engineering confidence scores must not be reported as probabilities.

### Runtime

- End-to-end latency.
- Per-stage latency.
- Peak memory.
- Route-memory size.
- Model size.
- Hardware, operating system, framework, and thread configuration.

## Baselines

At minimum compare:

- Random/majority branch baseline.
- Global centroid matching.
- Best-frame retrieval.
- Current component score.
- Best-window selection.
- Diverse top-k aggregation.
- A sequence baseline such as DTW where computationally practical.

For future fusion, compare visual-only, IMU-only, and fused systems.

## Ablations

- Original-only versus flip-aware embeddings.
- Overlapping versus disjoint segmentation.
- With and without temporal plausibility priors.
- Different window sizes and top-k values.
- With and without shared-path penalty.
- Different encoders.
- Different frame-sampling strategies.

## Leakage controls

- Never evaluate a route using the exact frames just inserted into memory and call it generalization.
- Do not tune thresholds on the final test set.
- Keep near-duplicate videos in the same split.
- Record all excluded/corrupt sessions and the reason for exclusion.
- Freeze the test manifest before final evaluation.

## Reproducibility record

Each experiment should preserve:

- Experiment ID and date.
- Git commit.
- Dataset and split manifest versions.
- Configuration snapshot.
- Model identifier/checksum.
- Dependency versions.
- Random seeds.
- Hardware information.
- Metrics and raw per-session decisions.
- Failure notes and deviations from protocol.

Use `research/protocols/experiment-template.md` before running a new experiment.
