from __future__ import annotations
import csv, io
from pathlib import Path
from vxn_ramnet.io.atomic import atomic_write_json, atomic_write_text
from vxn_ramnet.io.schema import validate_schema
from .sanitize import csv_cell, markdown_text

CSV_FIELDS=["query_id","decision_kind","branch_id","confidence","reason","branch_a_score","branch_b_score","branch_gap","common_score","junction_score","selected_windows"]

def write_csv(path:Path,rows:list[dict])->None:
    stream=io.StringIO(newline="")
    writer=csv.DictWriter(stream,fieldnames=CSV_FIELDS,extrasaction="ignore")
    writer.writeheader()
    for row in rows: writer.writerow({key:csv_cell(row.get(key,"")) for key in CSV_FIELDS})
    atomic_write_text(path,stream.getvalue())

def write_markdown(path:Path,summary:dict)->None:
    graph=summary["route_memory"]
    lines=["# VXN-RAMNet Run Report","","> Research prototype. Not a certified mobility or safety device and not a sole navigation source.","","## Run","",f"- Run ID: `{markdown_text(summary['run_id'])}`",f"- Schema: `{markdown_text(summary['schema_version'])}`",f"- Mode: constrained single-junction/two-branch camera baseline",f"- Segment policy: `{markdown_text(graph['segment_policy'])}`","","## Learned events","",f"- First junction frame: `{graph['events']['first_junction_index']}`",f"- Turnaround frame: `{graph['events']['turnaround_index']}`",f"- Return junction frame: `{graph['events']['return_junction_index']}`",f"- Junction confidence: `{markdown_text(graph['quality']['junction_confidence'])}`",f"- Backtrack confidence: `{markdown_text(graph['quality']['backtrack_confidence'])}`","","## Query decisions","","| Query | Decision | Branch | Confidence | A score | B score | Gap | Reason |","|---|---|---|---:|---:|---:|---:|---|"]
    for row in summary["query_results"]:
        confidence="" if row["confidence"] is None else f"{row['confidence']:.4f}"
        lines.append(f"| {markdown_text(row['query_id'])} | {markdown_text(row['decision_kind'])} | {markdown_text(row['branch_id'] or '')} | {confidence} | {row['branch_a_score']:.4f} | {row['branch_b_score']:.4f} | {row['branch_gap']:.4f} | {markdown_text(row['reason'])} |")
    lines += ["","## Interpretation boundary","","Branch A and Branch B are exploration-order labels. Physical left/right direction is not claimed until validated IMU turn detection is integrated.",""]
    atomic_write_text(path,"\n".join(lines))

def write_final_reports(report_dir:Path,summary:dict)->dict[str,str]:
    report_dir.mkdir(parents=True,exist_ok=True)
    paths={"json":report_dir/"summary.json","csv":report_dir/"query-results.csv","markdown":report_dir/"report.md"}
    summary = {**summary, "report_files": {key: value.as_posix() for key, value in paths.items()}}
    validate_schema("run-summary.schema.json", summary)
    atomic_write_json(paths["json"], summary)
    write_csv(paths["csv"], summary["query_results"])
    write_markdown(paths["markdown"], summary)
    return {key:value.as_posix() for key,value in paths.items()}
