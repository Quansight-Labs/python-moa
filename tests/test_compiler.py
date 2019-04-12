"""high level tests

"""
import pytest

from moa.frontend import LazyArray
from moa.compiler import compiler
from moa.array import Array


def test_lenore_example_1():
    _A = LazyArray(name='A', shape=(2, 3))
    _B = LazyArray(name='B', shape=(2, 3))
    python_source = compiler((_A + _B).T[0].context)
    print(python_source)

    local_dict = {}
    exec(python_source, globals(), local_dict)

    A = Array((2, 3), (1, 2, 3, 4, 5, 6))
    B = Array((2, 3), (7, 8, 9, 10, 11, 12))
    C = local_dict['f'](A, B)
    assert C.shape == (2,)
    assert C.value == [8, 14]


def test_lenore_example_1_symbols():
    _A = LazyArray(name='A', shape=('n', 'm'))
    _B = LazyArray(name='B', shape=('l', 3))
    python_source = compiler((_A + _B).T['i'].context)

    local_dict = {}
    exec(python_source, globals(), local_dict)

    A = Array((2, 3), (1, 2, 3, 4, 5, 6))
    B = Array((2, 3), (7, 8, 9, 10, 11, 12))
    i = Array((), (0))
    C = local_dict['f'](A=A, B=B, i=i)
    assert C.shape == (2,)
    assert C.value == [8, 14]
