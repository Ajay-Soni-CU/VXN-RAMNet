from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

class JsonLineHandler(logging.Handler):
    def __init__(self,path:Path): super().__init__(); self.path=path; path.parent.mkdir(parents=True,exist_ok=True)
    def emit(self,record:logging.LogRecord)->None:
        payload={"timestamp":datetime.now(timezone.utc).isoformat(),"level":record.levelname,"logger":record.name,"message":record.getMessage()}
        if hasattr(record,"event"): payload["event"]=record.event
        with self.path.open("a",encoding="utf-8") as handle: handle.write(json.dumps(payload,ensure_ascii=False)+"\n")

def configure_logging(level:str="INFO",jsonl_path:Path|None=None)->logging.Logger:
    logger=logging.getLogger("vxn_ramnet"); logger.handlers.clear(); logger.propagate=False; logger.setLevel(level)
    console=logging.StreamHandler(); console.setFormatter(logging.Formatter("[%(levelname)s] %(message)s")); logger.addHandler(console)
    if jsonl_path: logger.addHandler(JsonLineHandler(jsonl_path))
    return logger
