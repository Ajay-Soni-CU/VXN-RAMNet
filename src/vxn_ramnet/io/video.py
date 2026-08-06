from __future__ import annotations
from pathlib import Path
import cv2
import numpy as np
from vxn_ramnet.config.models import FrameSettings
from vxn_ramnet.core.exceptions import InputValidationError
from vxn_ramnet.core.types import VideoMetadata


def inspect_video(path: str | Path, settings: FrameSettings) -> VideoMetadata:
    source = Path(path)
    if not source.is_file():
        raise InputValidationError(f"Video not found: {source}")
    if source.suffix.lower() not in settings.allowed_extensions:
        raise InputValidationError(f"Unsupported video extension: {source.suffix}")
    size = source.stat().st_size
    if size <= 0 or size > settings.maximum_input_bytes:
        raise InputValidationError(f"Video size is invalid or exceeds limit: {size} bytes")
    cap = cv2.VideoCapture(str(source))
    try:
        if not cap.isOpened():
            raise InputValidationError(f"OpenCV could not open video: {source}")
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if not np.isfinite(fps) or fps <= 0 or total <= 0 or width <= 0 or height <= 0:
            raise InputValidationError(f"Invalid video metadata for: {source}")
        duration = total / fps
        if not np.isfinite(duration) or duration <= 0:
            raise InputValidationError(f"Invalid video duration for: {source}")
        return VideoMetadata(source.resolve(), fps, total, float(duration), width, height, size)
    finally:
        cap.release()


def extract_evenly_spaced_frames(path: str | Path, output_dir: str | Path, requested: int, max_seconds: float, settings: FrameSettings) -> dict:
    meta = inspect_video(path, settings)
    usable_total = min(meta.total_frames, max(1, int(min(meta.duration_seconds, max_seconds) * meta.fps)))
    actual_requested = min(requested, usable_total)
    indices = np.unique(np.linspace(0, usable_total - 1, actual_requested, dtype=np.int64))
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(meta.path))
    saved: list[str] = []
    failures: list[int] = []
    try:
        for order, frame_index in enumerate(indices, start=1):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(frame_index))
            ok, frame = cap.read()
            if not ok or frame is None:
                failures.append(int(frame_index)); continue
            output = target / f"frame-{order:05d}.jpg"
            write_ok = cv2.imwrite(str(output), frame, [cv2.IMWRITE_JPEG_QUALITY, settings.jpeg_quality])
            if not write_ok or not output.is_file():
                failures.append(int(frame_index)); continue
            saved.append(output.as_posix())
    finally:
        cap.release()
    minimum = max(1, int(len(indices) * settings.minimum_saved_ratio))
    if len(saved) < minimum:
        raise InputValidationError(f"Only {len(saved)}/{len(indices)} frames were saved from {meta.path}; failed indices={failures[:20]}")
    return {
        "video_path": meta.path.as_posix(), "fps": meta.fps, "duration_seconds": meta.duration_seconds,
        "total_frames": meta.total_frames, "usable_frames": usable_total, "requested_frames": requested,
        "sampled_unique_frames": len(indices), "saved_frames": len(saved), "failed_indices": failures,
        "frame_paths": saved, "width": meta.width, "height": meta.height, "file_size_bytes": meta.file_size_bytes,
    }
