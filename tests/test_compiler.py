"""Tests that guide development

1. [X] Demonstrate simple working parser
2. [ ] Handle symbolic shapes
3. [ ] Einsum implementation
"""
import pytest

from moa.compiler import compiler


def test_lenore_example_1():
    python_source = compiler('<0> psi (tran(A ^ <2 3> + B ^ <2 3>))')
    assert python_source == "(A[(_i3, 0)] + B[(_i3, 0)])"
