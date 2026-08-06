from __future__ import annotations
from importlib import metadata
from pathlib import Path
from typing import Sequence
import numpy as np
from vxn_ramnet.algorithms.similarity import l2_normalize_rows
from vxn_ramnet.config.models import EncoderSettings
from vxn_ramnet.core.exceptions import ModelLoadError
from vxn_ramnet.io.checksums import sha256_file
from vxn_ramnet.vision.preprocessing import load_rgb

class EfficientNetB0VisualEncoder:
    """Frozen Keras EfficientNetB0 embedding adapter.

    TensorFlow is imported lazily and remains an optional dependency.
    """
    def __init__(self, settings: EncoderSettings):
        self.settings=settings
        try:
            import tensorflow as tf
            from tensorflow.keras.applications import EfficientNetB0
            from tensorflow.keras.applications.efficientnet import preprocess_input
        except ImportError as exc:
            raise ModelLoadError("TensorFlow is required. Install with: pip install 'vxn-ramnet[vision]'") from exc
        self._tf=tf; self._preprocess=preprocess_input
        height,width=settings.input_size
        keras_weights=None if settings.weights=="local" else settings.weights
        if keras_weights=="imagenet" and not settings.allow_remote_weight_resolution:
            raise ModelLoadError("Remote/cache ImageNet weight resolution is disabled; provide a local weights_path")
        try:
            self._model=EfficientNetB0(input_shape=(height,width,3),include_top=False,weights=keras_weights,pooling="avg")
            if settings.weights=="local": self._model.load_weights(str(settings.weights_path))
            self._model.trainable=False
            self._model(np.zeros((1,height,width,3),dtype=np.float32),training=False)
        except Exception as exc:
            raise ModelLoadError(f"Could not initialize EfficientNetB0: {exc}") from exc
        self._manifest={
            "encoder":"efficientnet_b0","input_size":[height,width],"embedding_dimension":int(self._model.output_shape[-1]),
            "weights_source":str(settings.weights_path) if settings.weights_path else settings.weights,
            "weights_sha256":sha256_file(settings.weights_path) if settings.weights_path else None,
            "tensorflow_version":getattr(tf, "__version__", None) or metadata.version("tensorflow"), "trainable":False,
        }

    @property
    def manifest(self)->dict: return dict(self._manifest)

    def encode(self, frame_paths: Sequence[Path], *, flip: bool=False)->np.ndarray:
        if not frame_paths: raise ValueError("No frame paths were provided")
        chunks=[]
        for start in range(0,len(frame_paths),self.settings.batch_size):
            paths=frame_paths[start:start+self.settings.batch_size]
            batch=np.stack([load_rgb(path,self.settings.input_size,flip) for path in paths])
            batch=self._preprocess(batch)
            output=np.asarray(self._model(batch,training=False),dtype=np.float32)
            chunks.append(l2_normalize_rows(output))
        return np.vstack(chunks).astype(np.float32)
