import csv
import json

from vxn_ramnet.reporting.writers import write_final_reports


def test_final_json_contains_report_files_and_csv_is_neutralized(tmp_path):
    summary = {
        "schema_version": "1.0.0",
        "run_id": "run-test",
        "system": "VXN-RAMNet",
        "implementation_status": "camera-only constrained research baseline",
        "route_memory": {
            "artifact_schema_version": "1.0.0",
            "component_order": ["common_path", "junction", "branch_a", "backtrack", "branch_b"],
            "mode": "constrained_single_junction_backtracking",
            "topology_limit": "one junction and two exploration-order branches",
            "segment_policy": "disjoint",
            "events": {"first_junction_index": 1, "turnaround_index": 2, "return_junction_index": 3},
            "quality": {
                "junction_score": 0.8,
                "junction_confidence": "high",
                "backtrack_score": 0.7,
                "backtrack_confidence": "high",
            },
            "segments": {},
            "component_counts": {},
            "branch_label_note": "Exploration-order labels.",
            "encoder": {},
        },
        "query_results": [{
            "query_id": "query-a", "decision_kind": "known_branch", "branch_id": "=FORMULA",
            "confidence": 0.8, "reason": "ok|safe", "branch_a_score": 0.8, "branch_b_score": 0.6,
            "branch_gap": 0.2, "common_score": 0.2, "junction_score": 0.3, "selected_windows": 2, "evidence": {},
        }],
    }
    files = write_final_reports(tmp_path, summary)
    saved = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert saved["report_files"] == files
    with (tmp_path / "query-results.csv").open(encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle))
    assert row["branch_id"].startswith("'")
    assert "\\|" in (tmp_path / "report.md").read_text(encoding="utf-8")
