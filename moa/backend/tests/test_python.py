import astunparse
import pytest

from moa.ast import BinaryNode, UnaryNode, ArrayNode, MOANodeTypes
from moa.backend import export_backend_python


@pytest.mark.parametrize('tree,result', [
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
def test_backend_python(tree, result):
    ast = export_backend_python(tree)
    source = astunparse.unparse(ast)[:-1] # remove newline
    assert source == result
