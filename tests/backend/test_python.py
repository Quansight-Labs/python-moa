import ast

import astunparse
import pytest

from moa.ast import MOANodeTypes, BinaryNode, UnaryNode, ArrayNode, SymbolNode
from moa.backend import python_backend


@pytest.mark.parametrize('symbol_table, tree, expected_source', [
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None)},
     BinaryNode(MOANodeTypes.PLUS, (3, 4),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B')),
     '(A + B)'
    ),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None)},
     BinaryNode(MOANodeTypes.MINUS, (3, 4),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B')),
     '(A - B)'
    ),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None)},
     BinaryNode(MOANodeTypes.TIMES, (3, 4),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B')),
     '(A * B)'
    ),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None)},
     BinaryNode(MOANodeTypes.DIVIDE, (3, 4),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B')),
     '(A / B)'
    ),
])
def test_python_backend_unit(symbol_table, tree, expected_source):
    ast = python_backend(symbol_table, tree)
    source = astunparse.unparse(ast)[:-1] # remove newline
    assert source == expected_source


@pytest.mark.parametrize('symbol_table, tree, expected_source', [
    # Lenore Simple Example #1 06/01/2018
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      '_i3': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
      '_a4': SymbolNode(MOANodeTypes.ARRAY, shape=(2,), value=('_i3', 0))},
     BinaryNode(MOANodeTypes.PLUS, (3,),
                BinaryNode(MOANodeTypes.PSI, (3,),
                           ArrayNode(MOANodeTypes.ARRAY, (2,), '_a4'),
                           ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A')),
                BinaryNode(MOANodeTypes.PSI, (3,),
                           ArrayNode(MOANodeTypes.ARRAY, (2,), '_a4'),
                           ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B'))),
     "(A[('_i3', 0)] + B[('_i3', 0)])"
    )
])
def test_python_backend_integration(symbol_table, tree, expected_source):
    ast = python_backend(symbol_table, tree)
    source = astunparse.unparse(ast)[:-1] # remove newline
    assert source == expected_source
