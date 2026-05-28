import numpy as np

from venn_diagram_lab.cluster import cluster_set_order

_EPS = 1e-9


def test_average_linkage_leaf_order_on_two_clusters():
    D = np.array([  # noqa: N806
        [0.0, 0.2, 0.9, 0.8],
        [0.2, 0.0, 0.85, 0.75],
        [0.9, 0.85, 0.0, 0.1],
        [0.8, 0.75, 0.1, 0.0],
    ])
    co = cluster_set_order(D, method="average")
    assert co.leaf_order == [0, 1, 2, 3]
    assert len(co.merges) == 3  # noqa: PLR2004
    assert abs(co.merges[0].height - 0.1) < _EPS
    assert abs(co.merges[2].height - 0.825) < _EPS


def test_complete_linkage_height():
    D = np.array([  # noqa: N806
        [0.0, 0.2, 0.9, 0.8],
        [0.2, 0.0, 0.85, 0.75],
        [0.9, 0.85, 0.0, 0.1],
        [0.8, 0.75, 0.1, 0.0],
    ])
    co = cluster_set_order(D, method="complete")
    assert abs(co.merges[2].height - 0.9) < _EPS


def test_single_linkage_height():
    D = np.array([  # noqa: N806
        [0.0, 0.2, 0.9, 0.8],
        [0.2, 0.0, 0.85, 0.75],
        [0.9, 0.85, 0.0, 0.1],
        [0.8, 0.75, 0.1, 0.0],
    ])
    co = cluster_set_order(D, method="single")
    assert abs(co.merges[2].height - 0.75) < _EPS


def test_n_eq_2():
    D = np.array([[0.0, 0.5], [0.5, 0.0]])  # noqa: N806
    co = cluster_set_order(D, method="average")
    assert co.leaf_order == [0, 1]
    assert len(co.merges) == 1
    assert abs(co.merges[0].height - 0.5) < _EPS


def test_n_eq_1():
    D = np.array([[0.0]])  # noqa: N806
    co = cluster_set_order(D, method="average")
    assert co.leaf_order == [0]
    assert co.merges == []
