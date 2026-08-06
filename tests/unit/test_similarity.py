import numpy as np

from vxn_ramnet.algorithms.similarity import flip_aware_similarity, l2_normalize_rows, suppress_diagonal


def test_flip_aware_similarity_uses_best_orientation():
    a = l2_normalize_rows(np.array([[1.0, 0.0]], dtype=np.float32))
    af = l2_normalize_rows(np.array([[0.0, 1.0]], dtype=np.float32))
    b = l2_normalize_rows(np.array([[0.0, 1.0]], dtype=np.float32))
    bf = l2_normalize_rows(np.array([[-1.0, 0.0]], dtype=np.float32))
    score = flip_aware_similarity(a, af, b, bf)
    assert score.shape == (1, 1)
    assert score[0, 0] == 1.0


def test_diagonal_suppression_does_not_mutate_input():
    source = np.eye(4, dtype=np.float32)
    result = suppress_diagonal(source, radius=0)
    assert np.all(np.diag(result) == -1.0)
    assert np.all(np.diag(source) == 1.0)
