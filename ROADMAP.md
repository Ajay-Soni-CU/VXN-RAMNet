# Roadmap

VXN-RAMNet is being developed as a research prototype, not as a finished product. Work is ordered by evidence dependency:

1. Preserve the reproducible camera baseline.
2. Build a versioned dataset and annotation protocol.
3. Evaluate frame quality, encoders, event detection, segmentation, and branch decisions.
4. Calibrate uncertainty and unknown-route rejection on held-out data.
5. Measure and optimize runtime without changing validated behavior.
6. Define and simulate the time-synchronized multimodal packet protocol.
7. Validate IMU events independently, then evaluate visual-inertial fusion.
8. Migrate the validated runtime to Android.
9. Integrate the wearable sensor node and measure power, thermal, and link behavior.
10. Add safety supervision and accessible guidance only after fault and human-subject protocols exist.

The detailed acceptance criteria are in [docs/implementation-roadmap.md](docs/implementation-roadmap.md).
