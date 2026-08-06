# Research material

## Historical notebooks

The notebooks preserve the evolution of the project:

1. `01-visual-route-memory-baseline.ipynb` — initial visual route-memory experiment.
2. `02-unknown-route-memory-insertion.ipynb` — unknown-route insertion experiment. Its immediate re-evaluation uses the same inserted frames and therefore demonstrates memorization mechanics, not independent generalization.
3. `03-shared-prefix-two-route-dtw.ipynb` — two-video shared-prefix and DTW branch experiment.
4. `04-single-video-backtracking-branch-graph.ipynb` — one-video backtracking graph that became the modular baseline.

Notebook outputs and execution counts are stripped. The notebooks are historical research records, not the executable package and not authoritative evidence of generalization.

## New experiments

Before running a new experiment:

1. Copy `protocols/experiment-template.md` into a separate, date-stamped experiment record outside raw-data directories.
2. Define the research question, hypothesis, dataset version, split, metrics, configuration, and acceptance criteria before inspecting final-test results.
3. Save aggregate and per-session results, failure notes, environment information, and the exact Git commit.
4. Do not commit private participant data or raw journey videos.
