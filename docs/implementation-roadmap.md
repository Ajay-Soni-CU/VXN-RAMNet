# Implementation roadmap

This roadmap is intentionally evidence-gated. A phase is complete only when its verification artifacts exist; writing code alone is insufficient.

## Phase 0 — Preserve the camera baseline

**Goal:** keep one reproducible reference behavior while the research evolves.

Work:
- Run all unit, integration, and Notebook 4 regression tests on a clean environment.
- Record Python, dependency, operating-system, model, and configuration versions.
- Retain the original baseline configuration and expected regression indices.

Verification:
- `pytest` passes.
- A clean run produces a config snapshot, manifest, memory artifact, query decisions, and report.
- The Notebook 4 regression reproduces first junction 60, turnaround 134, and return junction 193 in legacy-compatible mode.

## Phase 1 — Establish the dataset protocol

**Goal:** replace anecdotal videos with a controlled research dataset.

Work:
- Define route, session, participant, device, lighting, weather, walking-speed, camera-height, and obstruction metadata.
- Define known-route, visually similar, partial-route, reverse-route, and unknown-route scenarios.
- Create consent, privacy, retention, anonymization, and deletion procedures before collecting participant data.
- Assign immutable route/session IDs and create a dataset manifest.

Verification:
- Every video maps to one manifest row.
- No raw participant data is committed to Git.
- Dataset splits can be regenerated from a versioned split manifest.
- The same physical route does not leak across evaluation boundaries unless the protocol explicitly tests repeat traversal.

## Phase 2 — Build an annotation and quality pipeline

**Goal:** obtain trustworthy ground truth and reject unusable inputs.

Work:
- Annotate junction arrival, branch entry, turnaround, junction revisit, and journey end.
- Add frame-quality measurements for blur, exposure, motion smear, dropped frames, and severe occlusion.
- Record annotation guidelines and inter-annotator agreement.

Verification:
- A second annotator can apply the guidelines consistently.
- Low-quality sequences are flagged before route inference.
- Quality-gate failures are reported with machine-readable reasons.

## Phase 3 — Benchmark the visual representation

**Goal:** determine whether EfficientNetB0 is an adequate embedding model.

Work:
- Compare the current encoder against at least one mobile-friendly alternative and one stronger reference model.
- Benchmark original-only versus flip-aware embeddings.
- Evaluate embedding dimension, storage, CPU latency, and memory use.
- Record model-source, license, preprocessing, weight checksum, and framework version.

Verification:
- A result table reports retrieval accuracy, route classification metrics, latency, memory, and artifact size.
- Model selection is justified by measured trade-offs, not popularity.
- The selected weight artifact has a documented checksum or immutable source identifier.

## Phase 4 — Validate event detection and segmentation

**Goal:** determine whether the heuristic junction and turnaround logic generalizes.

Work:
- Compare predicted event indices with annotations.
- Measure absolute frame/time error for first junction, turnaround, and return junction.
- Test sensitivity to temporal search ranges, window size, memory radius, and segment boundaries.
- Compare fixed priors with a less position-dependent candidate search.

Verification:
- Event-detection errors are reported on held-out routes.
- Failure examples are categorized.
- Segment overlap/leakage is measured.
- Default parameters are selected without using the final test set.

## Phase 5 — Calibrate branch, uncertainty, and unknown decisions

**Goal:** turn heuristic scores into empirically justified operating thresholds.

Work:
- Create separate calibration and final test sets.
- Evaluate known-branch accuracy, macro F1, unknown-route AUROC/AUPRC, false-known rate, abstention rate, and coverage-risk curves.
- Compare best-window, top-k aggregation, and sequential evidence accumulation.
- Add hysteresis and minimum-evidence rules where required.

Verification:
- Thresholds are derived only from calibration data.
- The final test set is evaluated once after threshold freezing.
- Results include confidence/reliability plots and false-guidance-oriented metrics.
- The system can abstain rather than force a branch prediction.

## Phase 6 — Improve performance without changing scientific behavior

**Goal:** establish bounded resource requirements for desktop and future mobile work.

Work:
- Profile frame extraction, encoding, similarity, memory construction, and classification separately.
- Reduce quadratic work through candidate selection, chunking, approximate retrieval, or incremental sequence memory where validated.
- Add embedding cache keys based on input checksum, model version, and preprocessing configuration.

Verification:
- Benchmark reports include wall time, peak memory, artifact size, and hardware details.
- Optimized output is compared against the reference implementation.
- Any numerical differences are quantified and accepted explicitly.

## Phase 7 — Design the multimodal packet contract

**Goal:** prepare VisionX integration without prematurely implementing the full wearable.

Work:
- Define image, IMU, ultrasonic, heartbeat, control, health, timestamp, sequence, and session fields.
- Define monotonic-clock behavior, clock-offset estimation, loss, duplicates, reordering, stale packets, and reconnect semantics.
- Build a desktop simulator that replays synchronized packets.

Verification:
- Schema validation rejects malformed packets.
- Automated tests cover loss, reorder, duplicates, stale data, and heartbeat expiry.
- The camera pipeline can consume simulated packets without wearable hardware.

## Phase 8 — Develop and validate the IMU research pipeline

**Goal:** identify movement events independently before fusion.

Work:
- Calibrate gyro and accelerometer bias.
- Implement gravity compensation and filtering.
- Estimate motion state and turn/turnaround events.
- Treat the magnetometer as optional and reject magnetically disturbed intervals.

Verification:
- Event metrics are reported against annotated IMU journeys.
- Stationary, walking, device-shake, and handheld-like artifact scenarios are tested.
- The pipeline outputs event confidence, quality, and rejection reasons.

## Phase 9 — Evaluate visual-inertial fusion

**Goal:** prove that fusion improves decisions rather than merely adding complexity.

Work:
- Time-align visual and IMU evidence.
- Preserve per-modality scores and quality flags.
- Compare visual-only, IMU-only, and fused systems.
- Implement explicit uncertain and degraded-sensor outcomes.

Verification:
- Held-out ablation demonstrates whether fusion reduces false-known decisions or improves event accuracy.
- Fusion never silently hides modality disagreement.
- Missing/degraded modality behavior is deterministic and tested.

## Phase 10 — Build the Android research runtime

**Goal:** migrate the validated pipeline incrementally to on-device execution.

Work:
- Select the model format after TFLite/ONNX/mobile benchmark results.
- Implement frame receiver, quality gate, embedding, bounded evidence buffer, route memory, and state machine.
- Store route memory locally with schema/version migration.

Verification:
- On-device latency, peak memory, temperature, and battery measurements are recorded.
- Desktop and Android outputs are compared on the same replayed sessions.
- The runtime operates offline and handles pause, stop, reconnect, and corrupted memory safely.

## Phase 11 — Integrate the wearable sensor node

**Goal:** connect measured hardware without moving route decisions onto the Raspberry Pi.

Work:
- Implement camera, protected ultrasonic input, IMU acquisition, hardware/software timestamps, packetization, and heartbeat.
- Measure Wi-Fi throughput, packet loss, CPU load, thermal behavior, and power use.
- Implement low-power/fail-safe behavior on link loss.

Verification:
- Electrical checks confirm HC-SR04 echo-level protection.
- Long-duration streaming logs contain no silent timestamp or sequence corruption.
- Disconnect tests stop stale guidance and enter the specified state.

## Phase 12 — Add safety supervision and accessible guidance

**Goal:** introduce guidance only after route and sensor evidence can be gated safely.

Work:
- Keep route decisions separate from obstacle warnings.
- Add cooldown, duplicate suppression, sensor-health gates, manual stop, and clear degraded states.
- Evaluate TTS timing and bone-conduction usability with appropriate ethics and supervision.

Verification:
- State-machine tests cover every allowed and forbidden transition.
- Fault injection proves link loss, sensor failure, stale data, low confidence, and internal errors suppress misleading route guidance.
- Human testing follows an approved protocol and never relies on VisionX as the sole navigation source.

## Phase 13 — Prepare research publication and hackathon evidence

**Goal:** present measurable work honestly and reproducibly.

Work:
- Publish architecture, dataset protocol, methods, baselines, ablations, metrics, failure cases, limitations, and demo evidence.
- Produce a deterministic demo route plus prerecorded fallback evidence.
- Keep implemented and proposed features visibly separated.

Verification:
- A fresh evaluator can install the repository, run tests, reproduce a sample experiment, and understand all unimplemented work.
- Every headline claim maps to a result table, test, measurement, or clearly labeled proposal.
