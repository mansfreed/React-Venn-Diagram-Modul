import numpy as np

from venn_diagram_lab.share_distribution import item_share_distribution


def test_empty_matrix_returns_zero_bins():
    m = np.zeros((0, 3), dtype=int)
    assert item_share_distribution(m) == {1: 0, 2: 0, 3: 0}


def test_three_set_matrix():
    m = np.array([
        [1, 0, 0],
        [1, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
        [1, 0, 1],
    ])
    assert item_share_distribution(m) == {1: 2, 2: 2, 3: 1}


def test_four_set_zero_bins_included():
    m = np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
    ])
    assert item_share_distribution(m) == {1: 2, 2: 0, 3: 0, 4: 0}


def test_zero_rows_are_skipped():
    m = np.array([
        [1, 0, 0],
        [0, 0, 0],
        [1, 1, 0],
    ])
    assert item_share_distribution(m) == {1: 1, 2: 1, 3: 0}
