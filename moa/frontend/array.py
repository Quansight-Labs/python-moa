from ..ast import (
    MOANodeTypes,
    ArrayNode, BinaryNode, UnaryNode, ReduceNode,
    add_symbol, generate_unique_array_name,
    join_symbol_tables
)


class LazyArray:
    def __init__(self, shape, value=None, name=None):
        self.symbol_table = {}
        self.tree = None

        if name is None and value is None:
            raise ValueError('either name or value must be supplied for LazyArray')

        if value is not None:
            raise NotImplemenetedError('not able to pass in value at compile time at this moment')

        shape = self._create_array_from_list_tuple(shape)
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

    def _create_array_from_int_float_string(self, value):
        if isinstance(value, str):
            array_name = value
            self.symbol_table = add_symbol(self.symbol_table, array_name, MOANodeTypes.ARRAY, (), None)
        else:
            array_name = generate_unique_array_name(self.symbol_table)
            self.symbol_table = add_symbol(self.symbol_table, array_name, MOANodeTypes.ARRAY, (), (value,))
        return ArrayNode(MOANodeTypes.ARRAY, None, array_name)

    def _create_array_from_list_tuple(self, value):
        if not any(isinstance(_, str) for _ in value):
            return value

        elements = ()
        for element in value:
            if isinstance(element, str):
                self.symbol_table = add_symbol(self.symbol_table, element, MOANodeTypes.ARRAY, (), None)
                elements = elements + (ArrayNode(MOANodeTypes.ARRAY, None, element),)
            else:
                elements = elements + (element,)
        return elements

    @property
    def T(self):
        return self.transpose()

    def transpose(self, transpose_vector=None):
        if transpose_vector is None:
            self.tree = UnaryNode(MOANodeTypes.TRANSPOSE, None, self.tree)
        else:
            symbolic_vector = self._create_array_from_list_tuple(transpose_vector)

            array_name = generate_unique_array_name(self.symbol_table)
            self.symbol_table = add_symbol(self.symbol_table, array_name, MOANodeTypes.ARRAY, (len(symbolic_vector),), tuple(symbolic_vector))
            self.tree = BinaryNode(MOANodeTypes.TRANSPOSEV, None,
                                   ArrayNode(MOANodeTypes.ARRAY, None, array_name),
                                   self.tree)
        return self

    def outer(self, operation, array):
        operation_map = {
            '+': (MOANodeTypes.DOT, MOANodeTypes.PLUS),
            '-': (MOANodeTypes.DOT, MOANodeTypes.MINUS),
            '*': (MOANodeTypes.DOT, MOANodeTypes.TIMES),
            '/': (MOANodeTypes.DOT, MOANodeTypes.DIVIDE),
        }
        if operation not in operation:
            raise ValueError(f'operation {operation} not in allowed operations (+-*/)')

        if isinstance(array, self.__class__):
            self.symbol_table, left_tree, right_tree = join_symbol_tables(self.symbol_table, self.tree, array.symbol_table, array.tree)
            self.tree = BinaryNode(operation_map[operation], None, left_tree, right_tree)
        elif isinstance(left, (int, float, str)):
            self.tree = BinaryNode(operation_map[operation], None,
                                   self.tree,
                                   self._create_array_from_int_float_string(array))
        else:
            raise TypeError(f'not known how to handle outer product with type {type(array)}')
        return self

    def reduce(self, operation):
        operation_map = {
            '+': (MOANodeTypes.REDUCE, MOANodeTypes.PLUS),
            '-': (MOANodeTypes.REDUCE, MOANodeTypes.MINUS),
            '*': (MOANodeTypes.REDUCE, MOANodeTypes.TIMES),
            '/': (MOANodeTypes.REDUCE, MOANodeTypes.DIVIDE),
        }
        if operation not in operation:
            raise ValueError(f'operation {operation} not in allowed operations (+-*/)')

        self.tree = ReduceNode(operation_map[operation], None, None, self.tree)
        return self

    def _rbinary_opperation(self, operation, left):
        if isinstance(left, self.__class__):
            self.symbol_table, left_tree, right_tree = join_symbol_tables(left.symbol_table, left.tree, self.symbol_table, self.tree)
            self.tree = BinaryNode(operation, None, left_tree, right_tree)
        elif isinstance(left, (int, float, str)):
            self.tree = BinaryNode(operation, None, self._create_array_from_int_float_string(left), self.tree)
        else:
            raise TypeError(f'not known how to handle binary operation with type {type(left)}')
        return self

    def _binary_opperation(self, operation, right):
        if isinstance(right, self.__class__):
            self.symbol_table, left_tree, right_tree = join_symbol_tables(self.symbol_table, self.tree, right.symbol_table, right.tree)
            self.tree = BinaryNode(operation, None, left_tree, right_tree)
        elif isinstance(right, (int, float, str)):
            self.tree = BinaryNode(operation, None, self.tree, self._create_array_from_int_float_string(right))
        else:
            raise TypeError(f'not known how to handle binary operation with type {type(right)}')
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

    def compile(self, backend='python', **kwargs):
        from ..compiler import compiler
        return compiler(self, frontend='array', backend=backend, **kwargs)

    def _repr_svg_(self):
        try:
            from ..visualize import visualize_ast
            dot = visualize_ast(self.symbol_table, self.tree)
            return dot.pipe(format='svg').decode(dot._encoding)
        except ImportError as e:
            return None
