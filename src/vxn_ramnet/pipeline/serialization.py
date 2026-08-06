from __future__ import annotations
from pathlib import Path
import numpy as np
from vxn_ramnet.core.types import EncodedSequence
from vxn_ramnet.io.atomic import atomic_write_json
from vxn_ramnet.io.npz import load_npz, save_npz


def save_encoded_sequence(sequence:EncodedSequence, arrays_path:Path, metadata_path:Path)->None:
    max_len=max(1,max((len(path) for path in sequence.frame_paths),default=1))
    save_npz(arrays_path,{"embeddings":sequence.embeddings.astype(np.float32),"flipped_embeddings":sequence.flipped_embeddings.astype(np.float32),"frame_paths":np.asarray(sequence.frame_paths,dtype=f"U{max_len}")})
    atomic_write_json(metadata_path,{"sequence_id":sequence.sequence_id,**sequence.metadata})


def load_encoded_sequence(sequence_id:str, arrays_path:Path, metadata_path:Path)->EncodedSequence:
    import json
    arrays=load_npz(arrays_path,{"embeddings","flipped_embeddings","frame_paths"})
    metadata=json.loads(metadata_path.read_text(encoding="utf-8"))
    if arrays["embeddings"].shape!=arrays["flipped_embeddings"].shape: raise ValueError("Original/flipped embedding shapes differ")
    if len(arrays["frame_paths"])!=len(arrays["embeddings"]): raise ValueError("Frame path count differs from embedding count")
    return EncodedSequence(sequence_id,arrays["embeddings"].astype(np.float32),arrays["flipped_embeddings"].astype(np.float32),tuple(arrays["frame_paths"].astype(str).tolist()),metadata)
