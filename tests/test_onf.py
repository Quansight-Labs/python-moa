import copy

import pytest

from moa.ast import (
    MOANodeTypes,
    BinaryNode, UnaryNode, ArrayNode, SymbolNode, FunctionNode, InitializeNode, LoopNode
)
from moa.onf import reduce_to_onf


@pytest.mark.parametrize("symbol_table, tree, expected_symbol_table, expected_tree", [
    # Lenore Simple Example #1 06/01/2018
    ({'_a0': SymbolNode(MOANodeTypes.ARRAY, (1,), (0,)),
      'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      '_i3': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
      '_a4': SymbolNode(MOANodeTypes.ARRAY, (1,), ('_i3',)),
      '_a5': SymbolNode(MOANodeTypes.ARRAY, shape=(2,), value=(0, '_i3')),
      '_a6': SymbolNode(MOANodeTypes.ARRAY, shape=(2,), value=('_i3', 0))},
      BinaryNode(MOANodeTypes.PLUS, (3,),
                 BinaryNode(MOANodeTypes.PSI, (3,),
                            ArrayNode(MOANodeTypes.ARRAY, (2,), '_a6'),
                            ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A')),
                 BinaryNode(MOANodeTypes.PSI, (3,),
                            ArrayNode(MOANodeTypes.ARRAY, (2,), '_a6'),
                            ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B'))),
     {'_a0': SymbolNode(MOANodeTypes.ARRAY, (1,), (0,)),
      'A': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      'B': SymbolNode(MOANodeTypes.ARRAY, (3, 4), None),
      '_i3': SymbolNode(MOANodeTypes.INDEX, (), (0, 3)),
      '_a4': SymbolNode(MOANodeTypes.ARRAY, (1,), ('_i3',)),
      '_a5': SymbolNode(MOANodeTypes.ARRAY, shape=(2,), value=(0, '_i3')),
      '_a6': SymbolNode(MOANodeTypes.ARRAY, shape=(2,), value=('_i3', 0)),
      '_a7': SymbolNode(MOANodeTypes.ARRAY, shape=(3,), value=None),
      '_a8': SymbolNode(MOANodeTypes.ARRAY, shape=(1,), value=('_i3',))},
     FunctionNode(MOANodeTypes.FUNCTION, (3,), ('B', 'A'), '_a7',
                  (InitializeNode(MOANodeTypes.INITIALIZE, (3,), '_a7'),
                   LoopNode(MOANodeTypes.LOOP, (3,), '_i3',
                            (BinaryNode(MOANodeTypes.ASSIGN, (3,),
                                        BinaryNode(MOANodeTypes.PSI, (3,),
                                                   ArrayNode(MOANodeTypes.ARRAY, (3,), '_a8'),
                                                   ArrayNode(MOANodeTypes.ARRAY, (3,), '_a7')),
                                        BinaryNode(MOANodeTypes.PLUS, (3,),
                                                   BinaryNode(MOANodeTypes.PSI, (3,),
                                                              ArrayNode(MOANodeTypes.ARRAY, (2,), '_a6'),
                                                              ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'A')),
                                                   BinaryNode(MOANodeTypes.PSI, (3,),
                                                              ArrayNode(MOANodeTypes.ARRAY, (2,), '_a6'),
                                                              ArrayNode(MOANodeTypes.ARRAY, (3, 4), 'B')))),))))),
])
def test_reduce_onf_integration(symbol_table, tree, expected_symbol_table, expected_tree):
    symbol_table_copy = copy.deepcopy(symbol_table)
    new_symbol_table, new_tree = reduce_to_onf(symbol_table, tree)
    assert symbol_table_copy == symbol_table
    assert new_symbol_table == expected_symbol_table
    assert new_tree == expected_tree
