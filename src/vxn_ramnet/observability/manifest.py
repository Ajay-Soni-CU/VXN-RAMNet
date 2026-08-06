from __future__ import annotations
import os, platform, sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Iterable
from vxn_ramnet.io.checksums import sha256_file
from vxn_ramnet.core.version import __version__

def dependency_versions(names:Iterable[str])->dict[str,str|None]:
    result={}
    for name in names:
        try: result[name]=metadata.version(name)
        except metadata.PackageNotFoundError: result[name]=None
    return result

def build_run_manifest(run_id:str,input_paths:dict[str,Path],model_manifest:dict|None=None)->dict:
    return {"run_id":run_id,"created_at":datetime.now(timezone.utc).isoformat(),"vxn_ramnet_version":__version__,
        "python":sys.version,"platform":platform.platform(),"machine":platform.machine(),"process_id":os.getpid(),
        "dependencies":dependency_versions(["numpy","opencv-python","Pillow","pydantic","PyYAML","tensorflow"]),
        "inputs":{key:{"path":path.as_posix(),"sha256":sha256_file(path),"bytes":path.stat().st_size} for key,path in input_paths.items()},
        "model":model_manifest,
    }
