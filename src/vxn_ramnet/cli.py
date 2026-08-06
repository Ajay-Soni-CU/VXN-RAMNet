from __future__ import annotations
import argparse
import json
from pathlib import Path
from vxn_ramnet.config import load_config
from vxn_ramnet.config.models import PipelineConfig
from vxn_ramnet.pipeline import VxnPipeline


def build_parser()->argparse.ArgumentParser:
    parser=argparse.ArgumentParser(prog="vxn-ramnet",description="VXN-RAMNet camera-only constrained route-memory research pipeline")
    sub=parser.add_subparsers(dest="command",required=True)
    run=sub.add_parser("run",help="Run the complete pipeline from a JSON/YAML config")
    run.add_argument("--config",required=True,type=Path)
    validate=sub.add_parser("validate-config",help="Validate and normalize a config without running")
    validate.add_argument("--config",required=True,type=Path)
    schema=sub.add_parser("print-config-schema",help="Print the current JSON schema")
    inspect=sub.add_parser("inspect-run",help="Print a concise run summary")
    inspect.add_argument("run_directory",type=Path)
    return parser


def main(argv:list[str]|None=None)->int:
    args=build_parser().parse_args(argv)
    if args.command=="run":
        result=VxnPipeline(load_config(args.config)).run()
        print(json.dumps({"run_id":result.run_id,"run_directory":result.run_directory.as_posix(),"report_files":result.report_files},indent=2)); return 0
    if args.command=="validate-config":
        config=load_config(args.config); print(json.dumps(config.model_dump(mode="json"),indent=2)); return 0
    if args.command=="print-config-schema":
        print(json.dumps(PipelineConfig.model_json_schema(),indent=2)); return 0
    if args.command=="inspect-run":
        summary=args.run_directory/"reports"/"summary.json"
        if not summary.is_file(): raise FileNotFoundError(f"Run summary not found: {summary}")
        data=json.loads(summary.read_text(encoding="utf-8"))
        print(json.dumps({"run_id":data.get("run_id"),"implementation_status":data.get("implementation_status"),"route_quality":data.get("route_memory",{}).get("quality",{}),"query_results":data.get("query_results",[])},indent=2)); return 0
    return 2

if __name__=="__main__": raise SystemExit(main())
