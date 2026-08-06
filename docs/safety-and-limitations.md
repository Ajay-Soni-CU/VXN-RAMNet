# Safety and limitations

## Intended use

The repository is intended for controlled research on visual route memory and branch recognition. It may support demonstrations, algorithm experiments, and future VisionX development.

## Prohibited interpretation

Do not present the current repository as:

- A certified mobility aid.
- A medical device.
- A collision-avoidance system.
- A complete navigation system.
- A validated real-time wearable.
- A replacement for a cane, guide dog, trained assistant, accessible navigation service, or human judgment.

## Current technical limitations

- Camera-only input.
- Offline full-video processing.
- Single-junction/two-branch topology.
- Exploration-order branch labels.
- Heuristic event detection and thresholds.
- No calibrated probability or safety confidence.
- No representative field dataset.
- No validated handling of crowds, traffic, stairs, drop-offs, moving obstacles, severe weather, low light, glare, or camera displacement.

## Future VisionX safety rules

- Link loss or stale packets must suppress route guidance.
- Sensor degradation must produce an explicit degraded/uncertain state.
- Ultrasonic distance must remain a supervisory warning channel, not proof of a safe path.
- Route inference and obstacle warning must remain separate evidence paths.
- Guidance must require validated route confidence, healthy required sensors, acceptable data freshness, and cooldown compliance.
- The user must have a clear manual stop mechanism.
- Human testing must use appropriate ethics, consent, supervision, and independent safety measures.

## Claim discipline

Use language such as “prototype,” “proposed,” “measured on the following dataset,” and “not yet validated.” Avoid “safe,” “accurate,” “reliable,” “production-grade,” or “works for visually impaired users” unless a specific, appropriate study supports the claim.
