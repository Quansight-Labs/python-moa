import ast

import astunparse
import pytest

from moa.ast import MOANodeTypes, BinaryNode, UnaryNode, ArrayNode, SymbolNode
from moa.backend import generate_python_source


@pytest.mark.parametrize('symbol_table, tree, expected_source', [
    # (+-/*)
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None)},
     BinaryNode(MOANodeTypes.PLUS, (3, 4),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B')),
     '(A + B)'),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None)},
     BinaryNode(MOANodeTypes.MINUS, (3, 4),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B')),
     '(A - B)'),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None)},
     BinaryNode(MOANodeTypes.TIMES, (3, 4),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B')),
     '(A * B)'),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None)},
     BinaryNode(MOANodeTypes.DIVIDE, (3, 4),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B')),
     '(A / B)'),
    # ==, !=, <, >, <=, >=
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (), (4,)),
      'B': SymbolNode(MOANodeTypes.ARRAY, (), (3,))},
     BinaryNode(MOANodeTypes.EQUAL, (),
                ArrayNode(MOANodeTypes.ARRAY, (), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (), 'B')),
      '(A == B)'),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (), (4,)),
      'B': SymbolNode(MOANodeTypes.ARRAY, (), (3,))},
     BinaryNode(MOANodeTypes.NOTEQUAL, (),
                ArrayNode(MOANodeTypes.ARRAY, (), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (), 'B')),
      '(A != B)'),
     ({'A': SymbolNode(MOANodeTypes.ARRAY, (), (4,)),
       'B': SymbolNode(MOANodeTypes.ARRAY, (), (3,))},
     BinaryNode(MOANodeTypes.LESSTHAN, (),
                ArrayNode(MOANodeTypes.ARRAY, (), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (), 'B')),
      '(A < B)'),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (), (4,)),
       'B': SymbolNode(MOANodeTypes.ARRAY, (), (3,))},
     BinaryNode(MOANodeTypes.LESSTHANEQUAL, (),
                ArrayNode(MOANodeTypes.ARRAY, (), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (), 'B')),
      '(A <= B)'),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (), (4,)),
       'B': SymbolNode(MOANodeTypes.ARRAY, (), (3,))},
     BinaryNode(MOANodeTypes.GREATERTHAN, (),
                ArrayNode(MOANodeTypes.ARRAY, (), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (), 'B')),
      '(A > B)'),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (), (4,)),
       'B': SymbolNode(MOANodeTypes.ARRAY, (), (3,))},
     BinaryNode(MOANodeTypes.GREATERTHANEQUAL, (),
                ArrayNode(MOANodeTypes.ARRAY, (), 'A'),
                ArrayNode(MOANodeTypes.ARRAY, (), 'B')),
      '(A >= B)'),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (), (4,)),
       'B': SymbolNode(MOANodeTypes.ARRAY, (), (3,))},
     BinaryNode(MOANodeTypes.GREATERTHANEQUAL, (),
                ArrayNode(MOANodeTypes.ARRAY, (), 'A'),
                BinaryNode(MOANodeTypes.PLUS, (),
                           ArrayNode(MOANodeTypes.ARRAY, (), 'A'),
                           ArrayNode(MOANodeTypes.ARRAY, (), 'B'))),
      '(A >= (A + B))'),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (), (4,)),
       'B': SymbolNode(MOANodeTypes.ARRAY, (), (3,))},
     BinaryNode(MOANodeTypes.AND, (),
                BinaryNode(MOANodeTypes.LESSTHAN, (),
                           ArrayNode(MOANodeTypes.ARRAY, (), 'A'),
                           ArrayNode(MOANodeTypes.ARRAY, (), 'B')),
                BinaryNode(MOANodeTypes.EQUAL, (),
                           ArrayNode(MOANodeTypes.ARRAY, (), 'B'),
                           ArrayNode(MOANodeTypes.ARRAY, (), 'A'))),
      '((A < B) and (B == A))'),
    ({'A': SymbolNode(MOANodeTypes.ARRAY, (), (4,)),
      'B': SymbolNode(MOANodeTypes.ARRAY, (), (3,))},
     BinaryNode(MOANodeTypes.OR, (),
                BinaryNode(MOANodeTypes.LESSTHAN, (),
                           ArrayNode(MOANodeTypes.ARRAY, (), 'A'),
                           ArrayNode(MOANodeTypes.ARRAY, (), 'B')),
                BinaryNode(MOANodeTypes.EQUAL, (),
                           ArrayNode(MOANodeTypes.ARRAY, (), 'B'),
                           ArrayNode(MOANodeTypes.ARRAY, (), 'A'))),
      '((A < B) or (B == A))'),
])
def test_python_backend_unit(symbol_table, tree, expected_source):
    assert expected_source == generate_python_source(symbol_table, tree)


def test_python_backend_materialize_scalar():
    symbol_table = {'A': SymbolNode(MOANodeTypes.ARRAY, (), (4,)),
                    'B': SymbolNode(MOANodeTypes.ARRAY, (), (3,))}

    tree = BinaryNode(MOANodeTypes.OR, (),
                      BinaryNode(MOANodeTypes.LESSTHAN, (),
                                 ArrayNode(MOANodeTypes.ARRAY, (), 'A'),
                                 ArrayNode(MOANodeTypes.ARRAY, (), 'B')),
                      BinaryNode(MOANodeTypes.EQUAL, (),
                                 ArrayNode(MOANodeTypes.ARRAY, (), 'B'),
                                 ArrayNode(MOANodeTypes.ARRAY, (), 'A')))

    assert generate_python_source(symbol_table, tree, materialize_scalars=True) == '((4 < 3) or (3 == 4))'


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
     "(A[(_i3, 0)] + B[(_i3, 0)])"
    )
])
def test_python_backend_integration(symbol_table, tree, expected_source):
    assert expected_source == generate_python_source(symbol_table, tree)
