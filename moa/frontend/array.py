from ..ast import (
    MOANodeTypes,
    ArrayNode, BinaryNode, UnaryNode,
    add_symbol, generate_unique_array_name,
    join_symbol_tables
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

    @property
    def T(self):
        return self.transpose()

    def transpose(self, vector=None):
        if vector is None:
            self.tree = UnaryNode(MOANodeTypes.TRANSPOSE, None, self.tree)
        else:
            raise NotImplementedError('arbitrary transpose not implemented yet')
        return self

    def _rbinary_opperation(self, operation, left):
        if isinstance(left, self.__class__):
            self.symbol_table, left_tree, right_tree = join_symbol_tables(left.symbol_table, left.tree, self.symbol_table, self.tree)
            self.tree = BinaryNode(operation, None, left_tree, right_tree)
        elif isinstance(left, (int, float)):
            array_name = generate_unique_array_name(self.symbol_table)
            self.symbol_table = add_symbol(self.symbol_table, array_name, MOANodeTypes.ARRAY, (), (left,))
            self.tree = BinaryNode(operation, None, ArrayNode(MOANodeTypes.ARRAY, None, array_name), self.tree)
        return self

    def _binary_opperation(self, operation, right):
        if isinstance(right, self.__class__):
            self.symbol_table, left_tree, right_tree = join_symbol_tables(self.symbol_table, self.tree, right.symbol_table, right.tree)
            self.tree = BinaryNode(operation, None, left_tree, right_tree)
        elif isinstance(right, (int, float)):
            array_name = generate_unique_array_name(self.symbol_table)
            self.symbol_table = add_symbol(self.symbol_table, array_name, MOANodeTypes.ARRAY, (), (right,))
            self.tree = BinaryNode(operation, None, self.tree, ArrayNode(MOANodeTypes.ARRAY, None, array_name))
        return self

    def __add__(self, other):
        return self._binary_opperation(MOANodeTypes.PLUS, other)

    def __radd__(self, other):
        return self._rbinary_opperation(MOANodeTypes.PLUS, other)

    def __sub__(self, other):
        return self._binary_opperation(MOANodeTypes.MINUS, other)

    def __rsub__(self, other):
        return self._rbinary_opperation(MOANodeTypes.MINUS, other)

    def __mul__(self, other):
        return self._binary_opperation(MOANodeTypes.TIMES, other)

    def __rmul__(self, other):
        return self._rbinary_opperation(MOANodeTypes.TIMES, other)

    def __truediv__(self, other):
        return self._binary_opperation(MOANodeTypes.DIVIDE, other)

    def __rtruediv__(self, other):
        return self._rbinary_opperation(MOANodeTypes.DIVIDE, other)

    def compile(self, backend='python'):
        from ..compiler import compiler
        return compiler(self, frontend='array', backend=backend)

    def _repr_svg_(self):
        try:
            from ..visualize import visualize_ast
            dot = visualize_ast(self.symbol_table, self.tree)
            return dot.pipe(format='svg').decode(dot._encoding)
        except ImportError as e:
            return None
