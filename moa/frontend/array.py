from ..ast import (
    MOANodeTypes,
    ArrayNode, BinaryNode, UnaryNode,
    add_symbol, generate_unique_array_name,
)


class LazyArray:
    def __init__(self, shape, value=None, name=None):
        self.symbol_table = {}
        self.tree = None

        name = name or generate_unique_array_name(self.symbol_table)
        self.symbol_table = add_symbol(self.symbol_table, name, MOANodeTypes.ARRAY, shape, value)
        self.tree = ArrayNode(MOANodeTypes.ARRAY, None, name)

    def __getitem__(self, index):
        array_name = generate_unique_array_name(self.symbol_table)
        if isinstance(index, int):
            indicies = (index,)
        else: # tuple
            indicies = ()
            for i in index:
                if not isinstance(i, int):
                    raise TypeError('expecting indexing arguments to be int or tuple of ints')
                else:
                    indicies = indicies + (i,)

        self.symbol_table = add_symbol(self.symbol_table, array_name, MOANodeTypes.ARRAY, (len(indicies),), indicies)
        self.tree = BinaryNode(MOANodeTypes.PSI, None,
                               ArrayNode(MOANodeTypes.ARRAY, None, array_name),
                               self.tree)
        return self

    def transpose(self):
        self.tree = UnaryNode(MOANodeTypes.TRANSPOSE, None, self.tree)
        return self
