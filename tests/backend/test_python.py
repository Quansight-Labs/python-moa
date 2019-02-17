import ast

import astunparse
import pytest

from moa.ast import BinaryNode, UnaryNode, ArrayNode, MOANodeTypes
from moa.backend import python_backend


@pytest.mark.parametrize('tree,result', [
    (BinaryNode(MOANodeTypes.PLUS, (3, 4),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A', None),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B', None)),
     '(A + B)'
    ),
    (BinaryNode(MOANodeTypes.MINUS, (3, 4),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A', None),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B', None)),
     '(A - B)'
    ),
    (BinaryNode(MOANodeTypes.TIMES, (3, 4),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A', None),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B', None)),
     '(A * B)'
    ),
    (BinaryNode(MOANodeTypes.DIVIDE, (3, 4),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A', None),
                ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B', None)),
     '(A / B)'
    ),
])
def test_python_backend_unit(tree, result):
    ast = python_backend(tree)
    source = astunparse.unparse(ast)[:-1] # remove newline
    assert source == result


@pytest.mark.parametrize('tree,result', [
    # Lenore Simple Example #1 06/01/2018
    (BinaryNode(MOANodeTypes.PLUS, (3,),
                BinaryNode(MOANodeTypes.PSI, (3,),
                           ArrayNode(MOANodeTypes.ARRAY, (2,), None, ('i0', 0)),
                           ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A', None)),
                BinaryNode(MOANodeTypes.PSI, (3,),
                           ArrayNode(MOANodeTypes.ARRAY, (2,), None, ('i0', 0)),
                           ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B', None))),
     "(A[('i0', 0)] + B[('i0', 0)])"
    )
])
def test_python_backend_integration(tree, result):
    ast = python_backend(tree)
    source = astunparse.unparse(ast)[:-1] # remove newline
    assert source == result
