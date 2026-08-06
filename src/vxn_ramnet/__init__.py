"""VXN-RAMNet camera-based visual route-memory research prototype.

The executable package implements only the constrained offline camera baseline.
VisionX wearable, IMU, Android, obstacle-supervision, and guidance components are
documented future work and are not represented as completed modules.
"""
from .config.models import PipelineConfig
from .pipeline.runner import PipelineResult, VxnPipeline, run_pipeline
from .core.version import __version__

__all__ = ["PipelineConfig", "PipelineResult", "VxnPipeline", "run_pipeline", "__version__"]
