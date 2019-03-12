import pytest

from moa.array import Array


def test_array_invalid_shape():
    Array(shape=(2, 3, 2), value=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))

    with pytest.raises(ValueError):
        Array(shape=(1, 2, 3), value=(1, 2), fmt='row')


def test_array_dimension():
    a = Array(shape=(1, 2, 3), value=(1, 2, 3, 4, 5, 6), fmt='row')

    assert len(a.shape) == 3


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


def test_array_scalar_opperations_invalid():
    a = Array(shape=(1, 2), value=(1, 2))

    with pytest.raises(TypeError):
        a + 1

    with pytest.raises(TypeError):
        1 + a

    with pytest.raises(TypeError):
        a - 1

    with pytest.raises(TypeError):
        1 - a

    with pytest.raises(TypeError):
        a * 1

    with pytest.raises(TypeError):
        1 * a

    with pytest.raises(TypeError):
        a / 1

    with pytest.raises(TypeError):
        1 / a


def test_array_scalar_opperations_valid():
    a = Array(shape=(), value=(3,))

    assert a + 1 == 4
    assert 1 + a == 4
    assert a - 1 == 2
    assert 1 - a == -2
    assert a * 1 == 3
    assert 1 * a == 3
    assert a / 1 == 3
    assert abs(1 / a - 0.3333333333333) < 1e-6


def test_array_scalar_comparison_invalid():
    a = Array(shape=(1, 2), value=(1, 2))

    with pytest.raises(TypeError):
        a > 1

    with pytest.raises(TypeError):
        1 > a

    with pytest.raises(TypeError):
        a >= 1

    with pytest.raises(TypeError):
        1 >= a

    with pytest.raises(TypeError):
        a < 1

    with pytest.raises(TypeError):
        1 < a

    with pytest.raises(TypeError):
        a <= 1

    with pytest.raises(TypeError):
        1 <= a

    with pytest.raises(TypeError):
        a == 1

    with pytest.raises(TypeError):
        1 == a

    with pytest.raises(TypeError):
        a != 1

    with pytest.raises(TypeError):
        1 != a


def test_array_scalar_comparison_valid():
    a = Array(shape=(), value=(3,))

    assert (a > 1) == True
    assert (1 > a) == False
    assert (a >= 1) == True
    assert (1 >= a) == False
    assert (a < 1) == False
    assert (1 < a) == True
    assert (a <= 1) == False
    assert (1 <= a) == True
    assert (a == 1) == False
    assert (1 == a) == False
    assert (a != 1) == True
    assert (1 != a) == True
