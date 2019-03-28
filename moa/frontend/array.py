from .. import ast
# from .. import compiler
from ..shape import calculate_shapes
# from ..dnf import reduce_to_dnf
# from ..onf import reduce_to_onf
# from ..analysis import metric_flops
from ..visualize import visualize_ast, print_ast

class LazyArray:
    def __init__(self, shape, value=None, name=None):
        if name is None and value is None:
            raise ValueError('either name or value must be supplied for LazyArray')

        if value is not None:
            raise NotImplemenetedError('not able to pass in value at compile time at this moment')

        shape = self._create_array_from_list_tuple(shape)
        name = name or ast.generate_unique_array_name(self.context)

        self.context = ast.create_context(ast=ast.Node((ast.NodeSymbol.ARRAY,), None, (name,), ()))
        self.context = ast.add_symbol(self.context, name, ast.NodeSymbol.ARRAY, shape, None, value)

    def __getitem__(self, index):
        if isinstance(index, (int, str, slice)):
            index = (index,)

        indicies = ()
        strides = ()
        for i in index:
            if isinstance(i, str):
                if strides:
                    raise IndexError('current limitation that indexing is not allowed past strides')
                self.context = ast.add_symbol(self.context, i, ast.NodeSymbol.ARRAY, (), None, None)
                indicies = indicies + (ast.Node((ast.NodeSymbol.ARRAY,), (), (i,), ()),)
            elif isinstance(i, int):
                if strides:
                    raise IndexError('current limitation that indexing is not allowed past strides')
                indicies = indicies + (i,)
            elif isinstance(i, slice):
                strides = strides + ((i.start, i.stop, i.step),)
            else:
                raise IndexError('only integers, symbols, and slices (`:`) are valid indicies')

        if indicies:
            array_name = ast.generate_unique_array_name(self.context)
            self.context = ast.add_symbol(self.context, array_name, ast.NodeSymbol.ARRAY, (len(indicies),), None, indicies)
            self.context = ast.create_context(
                ast=ast.Node((ast.NodeSymbol.PSI,), None, (), (ast.Node((ast.NodeSymbol.ARRAY,), None, (array_name,), ()), self.context.ast)),
                symbol_table=self.context.symbol_table)
        if strides:
            raise NotImplemenetedError('strides not implemented')
        return self

    def _create_array_from_int_float_string(self, value):
        if isinstance(value, str):
            array_name = value
            self.context = ast.add_symbol(self.context, array_name, ast.NodeSymbol.ARRAY, (), None, None)
        else:
            array_name = ast.generate_unique_array_name(self.context)
            self.context = add_symbol(self.context, array_name, ast.NodeSymbol.ARRAY, (), None, (value,))
        return ast.Node((ast.NodeSymbol.ARRAY,), None, (array_name,), ())

    def _create_array_from_list_tuple(self, value):
        if not any(isinstance(_, str) for _ in value):
            return value

        elements = ()
        for element in value:
            if isinstance(element, str):
                self.context = ast.add_symbol(self.context, element, NodeSymbol.ARRAY, (), None, None)
                elements = elements + (ast.Node((ast.NodeSymbol.ARRAY,), None, (element,), ()),)
            else:
                elements = elements + (element,)
        return elements

    @property
    def T(self):
        return self.transpose()

    def transpose(self, transpose_vector=None):
        if transpose_vector is None:
            self.context = ast.create_context(
                ast=ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (self.context.ast,)),
                symbol_table=self.context.symbol_table)
        else:
            symbolic_vector = self._create_array_from_list_tuple(transpose_vector)

            array_name = ast.generate_unique_array_name(self.context)
            self.context = ast.add_symbol(self.context, array_name, ast.NodeSymbol.ARRAY, (len(symbolic_vector),), None, tuple(symbolic_vector))
            self.context = ast.create_context(
                ast=ast.Node((ast.NodeSymbol.TRANSPOSEV,), None, (), (ast.Node((ast.NodeSymbol.ARRAY,), None, (array_name,), ()), self.context.ast)),
                symbol_table=self.context.symbol_table)
        return self

    # def outer(self, operation, array):
    #     operation_map = {
    #         '+': (NodeSymbol.DOT, NodeSymbol.PLUS),
    #         '-': (NodeSymbol.DOT, NodeSymbol.MINUS),
    #         '*': (NodeSymbol.DOT, NodeSymbol.TIMES),
    #         '/': (NodeSymbol.DOT, NodeSymbol.DIVIDE),
    #     }
    #     if operation not in operation:
    #         raise ValueError(f'operation {operation} not in allowed operations (+-*/)')

    #     if isinstance(array, self.__class__):
    #         self.symbol_table, left_tree, right_tree = join_symbol_tables(self.symbol_table, self.tree, array.symbol_table, array.tree)
    #         self.tree = Node(operation_map[operation], None, left_tree, right_tree)
    #     elif isinstance(left, (int, float, str)):
    #         self.tree = Node(operation_map[operation], None,
    #                                self.tree,
    #                                self._create_array_from_int_float_string(array))
    #     else:
    #         raise TypeError(f'not known how to handle outer product with type {type(array)}')
    #     return self

    def reduce(self, operation):
        operation_map = {
            '+': (ast.NodeSymbol.REDUCE, ast.NodeSymbol.PLUS),
            '-': (ast.NodeSymbol.REDUCE, ast.NodeSymbol.MINUS),
            '*': (ast.NodeSymbol.REDUCE, ast.NodeSymbol.TIMES),
            '/': (ast.NodeSymbol.REDUCE, ast.NodeSymbol.DIVIDE),
        }
        if operation not in operation:
            raise ValueError(f'operation {operation} not in allowed operations (+-*/)')

        self.context = ast.create_context(
            ast=ast.Node(operation_map[operation], None, (), (self.context.ast,)),
            symbol_table=self.context.symbol_table)
        return self

    # def _rbinary_opperation(self, operation, left):
    #     if isinstance(left, self.__class__):
    #         self.symbol_table, left_tree, right_tree = join_symbol_tables(left.symbol_table, left.tree, self.symbol_table, self.tree)
    #         self.tree = Node(operation, None, left_tree, right_tree)
    #     elif isinstance(left, (int, float, str)):
    #         self.tree = Node(operation, None, self._create_array_from_int_float_string(left), self.tree)
    #     else:
    #         raise TypeError(f'not known how to handle binary operation with type {type(left)}')
    #     return self

    # def _binary_opperation(self, operation, right):
    #     if isinstance(right, self.__class__):
    #         self.symbol_table, left_tree, right_tree = join_symbol_tables(self.symbol_table, self.tree, right.symbol_table, right.tree)
    #         self.tree = Node(operation, None, left_tree, right_tree)
    #     elif isinstance(right, (int, float, str)):
    #         self.tree = Node(operation, None, self.tree, self._create_array_from_int_float_string(right))
    #     else:
    #         raise TypeError(f'not known how to handle binary operation with type {type(right)}')
    #     return self

    # def __add__(self, other):
    #     return self._binary_opperation(NodeSymbol.PLUS, other)

    # def __radd__(self, other):
    #     return self._rbinary_opperation(NodeSymbol.PLUS, other)

    # def __sub__(self, other):
    #     return self._binary_opperation(NodeSymbol.MINUS, other)

    # def __rsub__(self, other):
    #     return self._rbinary_opperation(NodeSymbol.MINUS, other)

    # def __mul__(self, other):
    #     return self._binary_opperation(NodeSymbol.TIMES, other)

    # def __rmul__(self, other):
    #     return self._rbinary_opperation(NodeSymbol.TIMES, other)

    # def __truediv__(self, other):
    #     return self._binary_opperation(NodeSymbol.DIVIDE, other)

    # def __rtruediv__(self, other):
    #     return self._rbinary_opperation(NodeSymbol.DIVIDE, other)

    # def compile(self, backend='python', **kwargs):
    #     return compiler.compiler(self, frontend='array', backend=backend, **kwargs)

    def _shape(self):
        return calculate_shapes(self.symbol_table, self.tree)

    # def _dnf(self):
    #     return reduce_to_dnf(*self._shape())

    # def _onf(self):
    #     return reduce_to_onf(*self._dnf())

    # def analysis(self):
    #     shape_symbol_table, shape_tree = calculate_shapes(self.symbol_table, self.tree)
    #     dnf_symbol_table, dnf_tree = reduce_to_dnf(shape_symbol_table, shape_tree)

    #     return {
    #         'unoptimized_flops': metric_flops(shape_symbol_table, shape_tree),
    #         'optimized_flops': metric_flops(dnf_symbol_table, dnf_tree)
    #     }

    def visualize(self, stage=None, as_text=False):
        if stage not in {None, 'shape', 'dnf', 'onf'}:
            raise ValueError('stage must be "shape", "dnf", or "onf"')

        if stage is None:
            context = self.context
        else:
            context = getattr(self, f'_{stage}')()

        if as_text:
            print_ast(context)
        else:
            return visualize_ast(context)


    def _repr_svg_(self):
        try:
            from ..visualize import visualize_ast
            dot = visualize_ast(self.symbol_table, self.tree)
            return dot.pipe(format='svg').decode(dot._encoding)
        except ImportError as e:
            return None
