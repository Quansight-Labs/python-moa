import pytest

from moa.ast import MOANodeTypes
from moa.shape import calculate_shapes


@pytest.mark.parametrize("tree,result", [
    # Lenore Simple Example #1 06/01/2018
    ((MOANodeTypes.PSI, None,
      (MOANodeTypes.ARRAY, (1,), None, (0,)),
      (MOANodeTypes.TRANSPOSE, None,
       (MOANodeTypes.PLUS, None,
        (MOANodeTypes.ARRAY, (3, 4), 'A', None),
        (MOANodeTypes.ARRAY, (3, 4), 'B', None)))),
     (MOANodeTypes.PSI, (3,),
      (MOANodeTypes.ARRAY, (1,), None, (0,)),
      (MOANodeTypes.TRANSPOSE, (4, 3),
       (MOANodeTypes.PLUS, (3, 4),
        (MOANodeTypes.ARRAY, (3, 4), 'A', None),
        (MOANodeTypes.ARRAY, (3, 4), 'B', None))))),
])
def test_shape(tree, result):
    new_tree = calculate_shapes(tree)
    print(new_tree)
    assert new_tree == result
