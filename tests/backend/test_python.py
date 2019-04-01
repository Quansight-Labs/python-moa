import ast

import astunparse
import pytest

from moa import ast, backend


@pytest.mark.parametrize('symbol_table, tree, expected_source', [
    # (+-/*)
    (ast.NodeSymbol.PLUS, '+'),
    (ast.NodeSymbol.MINUS, '-'),
    (ast.NodeSymbol.TIMES, '*'),
    (ast.NodeSymbol.DIVIDE, '/'),
    # ==, !=, <, >, <=, >=
    (ast.NodeSymbol.EQUAL, '=='),
    (ast.NodeSymbol.NOTEQUAL, '!='),
    (ast.NodeSymbol.LESSTHAN, '<'),
    (ast.NodeSymbol.LESSTHANEQUAL, '<='),
    (ast.NodeSymbol.LESSTHAN, '>'),
    (ast.NodeSymbol.LESSTHANEQUAL, '>='),
])
def test_python_backend_unit(operation, operation_string):
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (4,)),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (3,))
    }
    tree = ast.Node((operation,), (3, 4), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (3, 4), ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), (3, 4), ('B',), ())))

    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    expected_source = f'(A {operation_string} B)'
    assert expected_source == backend.generate_python_source(context)


@pytest.mark.parametrize('symbol_table, tree, expected_source', [
    ({
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (4,)),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (3,))
    },
     ast.Node((ast.NodeSymbol.GREATERTHANEQUAL,), (), (), (
         ast.Node((ast.NodeSymbol.ARRAY,), (), ('A',), ()),
         ast.Node((ast.NodeSymbol.PLUS,), (), (), (
             ast.Node((ast.NodeSymbol.ARRAY,), (), ('A',), ()),
             ast.Node((ast.NodeSymbol.ARRAY,), (), ('B',), ()))))),
     '(A >= (A + B))'),
    ({
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (4,)),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (3,))
    },
     ast.Node((ast.NodeSymbol.AND,), (), (), (
         ast.Node((ast.NodeSymbol.LESSTHAN,), (), (), (
             ast.Node((ast.NodeSymbol.ARRAY,), (), ('A',), ()),
             ast.Node((ast.NodeSymbol.ARRAY,), (), ('B',), ()))),
         ast.Node((ast.NodeSymbol.EQUAL,), (), (), (
             ast.Node((ast.NodeSymbol.ARRAY,), (), ('B',), ()),
             ast.Node((ast.NodeSymbol.ARRAY,), (), ('A',), ()))))),
     '((A < B) and (B == A))'),
    ({
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (4,)),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (3,))
    },
     ast.Node((ast.NodeSymbol.OR,), (), (), (
         ast.Node((ast.NodeSymbol.LESSTHAN,), (), (), (
             ast.Node((ast.NodeSymbol.ARRAY,), (), ('A',), ()),
             ast.Node((ast.NodeSymbol.ARRAY,), (), ('B',), ()))),
         ast.Node((ast.NodeSymbol.EQUAL,), (), (), (
             ast.Node((ast.NodeSymbol.ARRAY,), (), ('B',), ()),
             ast.Node((ast.NodeSymbol.ARRAY,), (), ('A',), ()))))),
     '((A < B) or (B == A))'),
])
def test_python_backend_unit(symbol_table, tree, expected_source):
    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    assert expected_source == backend.generate_python_source(context)


def test_python_backend_materialize_scalar():
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (4,)),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (3,))
    }

    tree = ast.Node((ast.NodeSymbol.OR,), (), (), (
        ast.Node((ast.NodeSymbol.LESSTHAN,), (), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (), ('A',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (), ('B',), ()))),
        ast.Node((ast.NodeSymbol.EQUAL,), (), (), (
            ast.Node((ast.NodeSymbol.ARRAY,), (), ('B',), ()),
            ast.Node((ast.NodeSymbol.ARRAY,), (), ('A',), ())))))

    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    assert backend.generate_python_source(context, materialize_scalars=True) == '((4 < 3) or (3 == 4))'


@pytest.mark.parametrize('symbol_table, tree, expected_source', [
    # Lenore Simple Example #1 06/01/2018
    ({'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4), None, None),
      'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4), None, None),
      '_i3': ast.SymbolNode(ast.NodeSymbol.INDEX, (), None, (0, 3, 1)),
      '_a4': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (ast.Node((ast.NodeSymbol.ARRAY,), (), ('_i3',), ()), 0))},
     ast.Node((ast.NodeSymbol.PLUS,), (3,), (), (
         ast.Node((ast.NodeSymbol.PSI,), (3,), (), (
             ast.Node((ast.NodeSymbol.ARRAY,), (2,), ('_a4',), ()),
             ast.Node((ast.NodeSymbol.ARRAY,), (3, 4), ('A',), ()))),
         ast.Node((ast.NodeSymbol.PSI,), (3,), (), (
             ast.Node((ast.NodeSymbol.ARRAY,), (2,), ('_a4',), ()),
             ast.Node((ast.NodeSymbol.ARRAY,), (3, 4), ('B',), ()))))),
     "(A[(_i3, 0)] + B[(_i3, 0)])"
    )
])
def test_python_backend_integration(symbol_table, tree, expected_source):
    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    assert expected_source == backend.generate_python_source(context)
