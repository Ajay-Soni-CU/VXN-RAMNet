import numpy as np
import pytest

from vxn_ramnet.core.exceptions import ArtifactError
from vxn_ramnet.io.npz import load_npz, save_npz


def test_safe_npz_round_trip(tmp_path):
    path = tmp_path / "safe.npz"
    save_npz(path, {"values": np.eye(3, dtype=np.float32), "names": np.array(["a", "b"], dtype="U1")})
    loaded = load_npz(path, {"values", "names"})
    assert np.allclose(loaded["values"], np.eye(3))
    assert loaded["names"].tolist() == ["a", "b"]


def test_object_arrays_are_rejected(tmp_path):
    with pytest.raises(ArtifactError):
        save_npz(tmp_path / "unsafe.npz", {"values": np.array([{"x": 1}], dtype=object)})


def test_missing_required_key_is_rejected(tmp_path):
    path = tmp_path / "safe.npz"
    save_npz(path, {"values": np.array([1], dtype=np.int32)})
    with pytest.raises(ArtifactError):
        load_npz(path, {"missing"})
