"""Tests that guide development

1. [X] Demonstrate simple working parser
2. [ ] Handle symbolic shapes
3. [ ] Einsum implementation
"""
import pytest
import astunparse

from moa.frontend import MOAParser
from moa.visualize import visualize_ast, print_ast
from moa.shape import calculate_shapes
from moa.reduction import reduce_ast
from moa.backend import python_backend


def test_lenore_example_1():
    symbol_table, tree = MOAParser().parse('<0> psi (tran(A ^ <2 3> + B ^ <2 3>))')
    shape_symbol_table, shape_tree = calculate_shapes(symbol_table, tree)
    symbol_table, reduced_ast = reduce_ast(symbol_table, shape_tree)
    ast = python_backend(symbol_table, reduced_ast)
    assert astunparse.unparse(ast)[:-1] == "(A[('_i3', 0)] + B[('_i3', 0)])"
