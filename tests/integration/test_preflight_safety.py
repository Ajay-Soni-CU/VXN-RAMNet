from pathlib import Path

import pytest

from vxn_ramnet.config.models import PipelineConfig
from vxn_ramnet.pipeline.runner import VxnPipeline


def test_missing_input_does_not_delete_existing_marked_run(tmp_path):
    run_dir = tmp_path / "runs" / "run-existing"
    run_dir.mkdir(parents=True)
    (run_dir / ".vxn-run").write_text("managed\n", encoding="utf-8")
    protected = run_dir / "keep.txt"
    protected.write_text("must survive", encoding="utf-8")
    config = PipelineConfig.model_validate({
        "project_root": tmp_path,
        "learning_video": {"id": "learning", "path": "missing-learning.avi"},
        "query_videos": [{"id": "query-a", "path": "missing-query.avi"}],
        "frames": {"allowed_extensions": [".avi"]},
        "artifacts": {
            "output_root": "runs",
            "run_id": "run-existing",
            "overwrite_existing_run": True,
        },
    })
    with pytest.raises(Exception):
        VxnPipeline(config).run()
    assert protected.read_text(encoding="utf-8") == "must survive"
