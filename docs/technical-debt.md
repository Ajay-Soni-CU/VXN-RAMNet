# Technical-debt status

This document maps the retained VXN-RAMNet debt register to the research-prototype repository. “Contained” means the immediate failure mode is reduced; it does not mean the broader product requirement is finished.

| ID | Topic | Current status | Evidence or next action |
|---|---|---|---|
| VX-01 | Unsafe output deletion | Contained | Deletion is limited to a marked run under the configured output root; retain destructive-path tests |
| VX-02 | Shared Streamlit storage | Contained for local use | Per-session temporary directories exist; authenticated hosted multi-user isolation is not implemented |
| VX-03 | Upload validation and DoS | Partially contained | Size/extension/decode checks exist; hosted quotas, request limits, and adversarial media testing remain |
| VX-04 | Unsafe NumPy deserialization | Contained | `allow_pickle=False`, object-array rejection, and corruption tests |
| VX-05 | Model provenance | Partial | Encoder metadata exists; approved weight checksum/immutable model manifest remains |
| VX-06 | Configuration validation | Contained for current schema | Strict Pydantic models; update tests whenever fields are added |
| VX-07 | Quadratic and synchronous performance | Open | Add stage profiling, candidate reduction, caching, and mobile resource benchmarks |
| VX-08 | Scenario-specific topology and temporal priors | Open | Evaluate wider topologies and reduce fixed-position assumptions |
| VX-09 | Tests, calibration, and scientific evaluation | Partial | Engineering tests exist; representative held-out evaluation and calibration remain the highest research priority |
| VX-10 | Dependency/build reproducibility | Partial | `pyproject.toml` defines supported ranges; lock or record exact experiment environments |
| VX-11 | Hosted authentication/authorization | Not in current scope | Required before any hosted service; local runner makes no hosted-service claim |
| VX-12 | Privacy and data lifecycle | Open before participant collection | Create consent, retention, access, anonymization, and deletion procedures |
| VX-13 | Durable job platform | Not in current scope | Required only if converted into a multi-user service |
| VX-14 | Observability | Partial | Local structured logs, manifests, and stage states exist; no centralized operational monitoring |
| VX-15 | Backup/disaster recovery | Not in current scope | Define for any future hosted dataset or service |
| VX-16 | Silent frame failures | Contained for common cases | Unique sampling, write checks, saved-ratio checks; expand corrupted-media fixtures |
| VX-17 | Documentation drift | Active control | Focused docs distinguish current baseline and proposed VisionX; review at each release |
| VX-18 | Report injection and error disclosure | Contained locally | CSV formula neutralization, Markdown escaping, and redacted UI errors; continue fuzz testing |
| VX-19 | Accessibility and over-trust | Open | Requires supervised user research, uncertainty UX, and false-guidance analysis |
| VX-20 | Notebook audit and output hygiene | Contained | Historical notebooks are output-stripped and labeled non-runtime; preserve leakage warning for Notebook 2 |

## Additional debts tracked explicitly

- EfficientNetB0 input behavior must remain consistent with configured dimensions.
- Query and upload identifiers must remain unique to prevent artifact overwrite.
- Inputs must be validated before managed output replacement.
- Saved final JSON must include complete report-file metadata.
- Schema compatibility must be tested as artifacts evolve.
- Segment-boundary leakage and best-window selection bias require measured evaluation.
- Current thresholds are not calibrated.
- The backtrack component is stored but not yet used directly in query classification.
- Physical left/right labels are unsupported until validated IMU turn evidence exists.
- Real-time execution, Android deployment, sensor fusion, and assistive safety remain future work.
