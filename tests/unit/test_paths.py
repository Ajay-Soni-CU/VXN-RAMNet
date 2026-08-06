import pytest

from vxn_ramnet.core.exceptions import ConfigurationError
from vxn_ramnet.io.paths import prepare_run_directory


def test_run_directory_requires_safe_identifier(tmp_path):
    with pytest.raises(ConfigurationError):
        prepare_run_directory(tmp_path, "../escape", False)


def test_existing_unmarked_directory_is_never_deleted(tmp_path):
    target = tmp_path / "run-test"
    target.mkdir()
    (target / "important.txt").write_text("keep", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        prepare_run_directory(tmp_path, "run-test", True)
    assert (target / "important.txt").read_text(encoding="utf-8") == "keep"


def test_marked_run_can_be_explicitly_replaced(tmp_path):
    target = prepare_run_directory(tmp_path, "run-test", False)
    (target / "old.txt").write_text("old", encoding="utf-8")
    replacement = prepare_run_directory(tmp_path, "run-test", True)
    assert replacement == target
    assert not (replacement / "old.txt").exists()
