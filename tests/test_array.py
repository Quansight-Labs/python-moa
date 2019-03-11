import pytest

from moa.array import Array


def test_array_invalid_shape():
    Array(shape=(2, 3, 2), value=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))

    with pytest.raises(ValueError):
        Array(shape=(1, 2, 3), value=(1, 2), fmt='row')


def test_array_dimension():
    a = Array(shape=(1, 2, 3), value=(1, 2, 3, 4, 5, 6), fmt='row')

    assert a.dimension == 3


def test_array_get_index():
    a = Array(shape=(1, 2, 3), value=(1, 2, 3, 4, 5, 6), fmt='row')
    assert a[0, 0, 0] == 1
    assert a[0, 0, 1] == 2
    assert a[0, 0, 2] == 3
    assert a[0, 1, 0] == 4
    assert a[0, 1, 2] == 6

    # partial index
    with pytest.raises(IndexError):
        a[1, 1]

    # out of bounds index
    with pytest.raises(IndexError):
        a[1, 1, 1] == 10


def test_array_set_index():
    a = Array(shape=(1, 2, 3), value=(1, 2, 3, 4, 5, 6), fmt='row')
    a[0, 1, 1] = 10
    a[0, 1, 1] == 10
