<h1 align="center">VXN-RAMNet</h1> 
 
<p align="center">
  <strong>VisionX Routine Adaptive Memory Network</strong><br>
  GPS-free visual route memory, backtracking branch-graph learning, and assistive navigation research.
</p>


<p align="center">
  <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/AjaySoni-Dev/VXN-RAMNet?style=social">
  <img alt="GitHub forks" src="https://img.shields.io/github/forks/AjaySoni-Dev/VXN-RAMNet?style=social">
</p>

<p align="center">
  <img alt="Status" src="https://img.shields.io/badge/status-research%20prototype-blue">
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-3776AB">
  <img alt="Encoder" src="https://img.shields.io/badge/encoder-EfficientNetB0-lightgrey">
  <img alt="Core" src="https://img.shields.io/badge/core-visual%20route%20memory-purple">
  <img alt="Deployment" src="https://img.shields.io/badge/runtime-offline%20experiments-orange">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>

<p align="center">
  <a href="#overview">Overview</a> ·
  <a href="#what-this-repo-contains">Contents</a> ·
  <a href="#implemented-system">Implemented</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#outputs">Outputs</a> ·
  <a href="#roadmap">Roadmap</a>
</p>

---

## Overview

**VXN-RAMNet** stands for **VisionX Routine Adaptive Memory Network**. It is a research prototype for learning routes from camera/video input without depending on GPS. The project extracts route frames, generates visual embeddings, stores memory of the route, detects repeated or backtracked sections, and classifies new query videos against the learned route memory.

The core workflow is:

```text
Route video → Frame extraction → EfficientNetB0 embeddings → Visual route memory → Branch graph → Query classification
```

The repository is focused on offline experiments, reproducible notebooks, modular Python source code, and generated reports that explain how the route was understood.

> [!IMPORTANT]
> This is a research prototype. It is not a certified navigation product, mobility-aid product, or safety-critical guidance system.

---

## What This Repo Contains

This repository is not only a notebook dump. It contains a complete experimental structure around the VXN-RAMNet idea:

| Area | What is included |
|---|---|
| Research notebooks | Four main notebooks for baseline memory, unknown-route learning, DTW branch learning, and backtracking branch-graph learning. |
| Modular source code | Reusable Python modules under `src/vxn_ramnet/` for extraction, embeddings, similarity, graph learning, classification, memory, and reports. |
| CLI runner | Script-based execution through `scripts/run_backtracking_pipeline.py`. |
| Optional UI | Streamlit upload app for testing learning/query videos from a browser. |
| Config files | Dependency lists and example JSON config under `configs/`. |
| Documentation | Architecture, build manual, full/short system flow, local usage guide, and future work notes. |
| Sample outputs | Example NPZ, JSON, CSV, and Markdown reports generated from the backtracking graph pipeline. |

---

## Implemented System

| Feature | Status | Notes |
|---|---:|---|
| Video frame extraction | ✅ Implemented | Extracts evenly spaced frames from learning and query videos. |
| Frozen visual encoder | ✅ Implemented | Uses EfficientNetB0-style embedding generation for route frames. |
| Baseline route memory | ✅ Implemented | Stores route-level visual evidence for similarity-based recognition. |
| Unknown-route learning | 🧪 Experimental | Explores when a query should be treated as unfamiliar. |
| Shared-prefix branch graph | ✅ Implemented | Uses route alignment/DTW ideas to detect shared and divergent path sections. |
| Backtracking branch graph | ✅ Stable advanced method | Learns graph-like route structure from one backtracking-style learning video. |
| Flip-aware comparison | ✅ Implemented | Uses original and flipped-frame evidence to improve matching. |
| Query branch classification | ✅ Implemented | Classifies query videos using multi-window similarity evidence. |
| Report generation | ✅ Implemented | Saves JSON, CSV, Markdown, and NPZ output files. |
| Live Android navigation | 🚧 Future work | Not implemented in this repository yet. |

---

## Main Experiments

| Notebook | Purpose |
|---|---|
| `experiments/01_route_memory_baseline.ipynb` | First route-memory baseline using frame extraction, embeddings, and similarity matching. |
| `experiments/02_unknown_route_auto_learning.ipynb` | Tests unknown-route handling and possible memory update behavior. |
| `experiments/03_shared_prefix_branch_graph_dtw.ipynb` | Learns shared-prefix and branch structure between route videos using DTW-style alignment. |
| `experiments/04_backtracking_branch_graph_learning.ipynb` | Main advanced notebook for one-video backtracking branch graph learning and branch classification. |

Use the notebooks when you want to understand the research step-by-step. Use the `src/` pipeline when you want a cleaner and repeatable execution flow.

---

## Modular Pipeline Flow

The stable workflow is available inside `src/vxn_ramnet/` and can be executed through scripts.

```text
Learning video + query videos
        ↓
Frame extraction
        ↓
Original + flipped visual embeddings
        ↓
Self-similarity analysis
        ↓
Junction revisit and turnaround detection
        ↓
Backtracking graph construction
        ↓
Component centroid memory
        ↓
Multi-window query classification
        ↓
Final report bundle
```

Important modules:

| Module | Role |
|---|---|
| `frame_extraction.py` | Locates videos, reads metadata, and extracts frames. |
| `encoder.py` | Builds visual embeddings for route frames. |
| `similarity.py` | Computes similarity matrices, moving averages, centroid scores, and component evidence. |
| `backtracking_graph.py` | Detects revisit/turnaround regions and builds route components. |
| `query_classifier.py` | Scores query videos against the learned route graph. |
| `route_memory.py` | Saves and loads reusable graph memory as NPZ files. |
| `reports.py` | Writes human-readable and machine-readable reports. |
| `pipeline.py` / `cli.py` | Connects the full workflow into an end-to-end runner. |

---

## Quick Start

Create a virtual environment and install the pipeline dependencies:

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\activate
pip install -r configs/requirements-src.txt
python scripts/run_backtracking_pipeline.py `
  --learning-video "path\to\learning_route.mp4" `
  --query-videos "path\to\query_route_1.mp4" "path\to\query_route_2.mp4"
```

macOS / Linux:

```bash
source .venv/bin/activate
pip install -r configs/requirements-src.txt
python scripts/run_backtracking_pipeline.py \
  --learning-video "path/to/learning_route.mp4" \
  --query-videos "path/to/query_route_1.mp4" "path/to/query_route_2.mp4"
```

Optional Streamlit upload UI:

```bash
pip install -r configs/requirements-ui.txt
streamlit run scripts/backtracking_upload_app.py
```

---

## Expected Inputs

| Input | Meaning |
|---|---|
| Learning video | A route recording used to build the visual memory and branch graph. |
| Query video | A new route clip that should be compared against the learned memory. |
| Config file | Optional JSON-style settings for thresholds, output paths, and execution behavior. |

For best results, videos should have stable camera motion, enough overlap with the learned route, and reasonable lighting consistency.

---

## Outputs

The pipeline writes a report bundle into `vxn_backtracking_graph_outputs/`.

| Output | Purpose |
|---|---|
| `frame_extraction_report.json` | Frame counts, metadata, and extraction details. |
| `vxn_backtracking_embeddings.npz` | Saved learning/query embeddings. |
| `vxn_backtracking_graph_memory.npz` | Saved graph memory, components, and centroids. |
| `vxn_backtracking_graph_metadata.json` | Detected segments, scores, and component details. |
| `query_reports/` | Per-query branch classification reports. |
| `vxn_backtracking_all_query_summary.json` | Combined query result summary. |
| `vxn_backtracking_final_summary.json` | Compact final summary. |
| `vxn_backtracking_query_results.csv` | Tabular result export. |
| `vxn_backtracking_report.md` | Human-readable Markdown report. |

---

## Repository Structure

```text
VXN-RAMNet/
├── configs/              # Dependency lists and example pipeline config
├── demo_outputs/         # Example console/demo output
├── docs/                 # Architecture, build manual, and system-flow docs
├── experiments/          # Main research notebooks
├── research_notes/       # Future work and research direction
├── sample_data/          # Input data guidance
├── sample_results/       # Example generated outputs
├── scripts/              # CLI runner and Streamlit app
├── src/vxn_ramnet/       # Modular implementation
├── SRC_PIPELINE_USAGE.md # Local usage guide
├── requirements.txt
├── README.md
└── LICENSE
```

---

## Roadmap

- Improve robustness on difficult lighting, blur, and partial route overlap.
- Add stronger multi-junction graph handling.
- Add a larger evaluation dataset and metrics report.
- Prepare lightweight/mobile inference experiments.
- Add object-detection or risk-awareness as a separate safety layer.

---

## Limitations

- Branch names are generated by exploration order and may need manual naming.
- Classification quality depends on the learning video, query coverage, frame rate, and route similarity.
- The current system is meant for offline route-memory experiments, not live public navigation.

---

## License

Released under the MIT License.
