from pathlib import Path

import pytest
from pydantic import ValidationError

from vxn_ramnet.config.models import PipelineConfig, VideoInput


def base_config(**changes):
    payload = {
        "learning_video": VideoInput(id="learning", path=Path("learning.mp4")),
        "query_videos": [VideoInput(id="query-a", path=Path("query.mp4"))],
        **changes,
    }
    return PipelineConfig(**payload)


def test_default_branch_labels_do_not_claim_physical_direction():
    config = base_config()
    assert config.branch_a_name == "BRANCH_A"
    assert config.branch_b_name == "BRANCH_B"


def test_duplicate_sequence_ids_are_rejected():
    with pytest.raises(ValidationError):
        base_config(query_videos=[VideoInput(id="learning", path=Path("query.mp4"))])


def test_duplicate_branch_names_are_rejected():
    with pytest.raises(ValidationError):
        base_config(branch_a_name="same", branch_b_name="same")


def test_project_root_cannot_be_output_root(tmp_path):
    with pytest.raises(ValidationError):
        base_config(project_root=tmp_path, artifacts={"output_root": tmp_path})
