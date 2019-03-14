import pytest

from moa.frontend import LazyArray
from moa.array import Array


@pytest.mark.xfail
def test_array_reduction():
    _A = LazyArray(name='A', shape=(3, 2))

    expression = _A.reduce('+')

    local_dict = {}
    exec(expression.compile(), globals(), local_dict)

    A = Array(shape=(3, 2), value=(1, 2, 3, 4, 5, 6))
    B = local_dict['f'](A=A)

    assert B.shape == (3,)
    assert B.value == [3, 7, 11]


def test_array_frontend_transpose_vector_outer_scalar_addition():
    _A = LazyArray(name='A', shape=(3, 2))
    _B = LazyArray(name='B', shape=(4,))
    _C = LazyArray(name='C', shape=(3, 4))

    expression = (((_A.T)[0] - 1).outer('*', _B) + _C + 'n').transpose([1, 0])

    local_dict = {}
    exec(expression.compile(), globals(), local_dict)

    A = Array(shape=(3, 2), value=(1, 2, 3, 4, 5, 6))
    B = Array(shape=(4,), value=(13, 14, 15, 16))
    C = Array(shape=(3, 4), value=(17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28))
    n = Array(shape=(), value=(4,))

    D = local_dict['f'](A=A, B=B, C=C, n=n)

    assert D.shape == (4, 3)
    assert D.value == [21, 51, 81, 22, 54, 86, 23, 57, 91, 24, 60, 96]
