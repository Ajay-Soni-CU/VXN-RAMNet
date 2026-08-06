from pathlib import Path

import cv2
import numpy as np

from vxn_ramnet.config.models import FrameSettings
from vxn_ramnet.io.video import extract_evenly_spaced_frames


def make_video(path: Path, count: int) -> None:
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10.0, (32, 24))
    assert writer.isOpened()
    for index in range(count):
        writer.write(np.full((24, 32, 3), index, dtype=np.uint8))
    writer.release()


def test_sampling_more_frames_than_available_never_duplicates_indices(tmp_path):
    source = tmp_path / "small.avi"
    make_video(source, 10)
    report = extract_evenly_spaced_frames(
        source,
        tmp_path / "frames",
        requested=30,
        max_seconds=10,
        settings=FrameSettings(allowed_extensions=(".avi",)),
    )
    assert report["sampled_unique_frames"] == 10
    assert report["saved_frames"] == 10
    assert len(set(report["frame_paths"])) == 10
