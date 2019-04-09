from .. import ast, compiler
from ..shape import calculate_shapes
from ..dnf import reduce_to_dnf
from ..onf import reduce_to_onf
from ..analysis import metric_flops
from ..visualize import visualize_ast, print_ast


class LazyArray:
    OPPERATION_MAP = {
        '+': ast.NodeSymbol.PLUS,
        '-': ast.NodeSymbol.MINUS,
        '*': ast.NodeSymbol.TIMES,
        '/': ast.NodeSymbol.DIVIDE,
    }

    def __init__(self, shape, value=None, name=None):
        if name is None and value is None:
            raise ValueError('either name or value must be supplied for LazyArray')

        if value is not None:
            raise NotImplemenetedError('not able to pass in value at compile time at this moment')

        self.context = ast.create_context()

        shape = self._create_array_from_list_tuple(shape)
        name = name or ast.generate_unique_array_name(self.context)

        self.context = ast.create_context(
            ast=ast.Node((ast.NodeSymbol.ARRAY,), None, (name,), ()),
            symbol_table=self.context.symbol_table)
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
            self.context = ast.add_symbol(self.context, array_name, ast.NodeSymbol.ARRAY, (), None, (value,))
        return ast.Node((ast.NodeSymbol.ARRAY,), None, (array_name,), ())

    def _create_array_from_list_tuple(self, value):
        if not any(isinstance(_, str) for _ in value):
            return value

        elements = ()
        for element in value:
            if isinstance(element, str):
                self.context = ast.add_symbol(self.context, element, ast.NodeSymbol.ARRAY, (), None, None)
                elements = elements + (ast.Node((ast.NodeSymbol.ARRAY,), (), (element,), ()),)
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

    def outer(self, operation, array):
        if operation not in self.OPPERATION_MAP:
            raise ValueError(f'operation {operation} not one of allowed operations {self.OPPERATION_MAP.keys()}')

        moa_operation = (ast.NodeSymbol.DOT, self.OPPERATION_MAP[operation])

        if isinstance(array, self.__class__):
            new_symbol_table, left_context, right_context = ast.join_symbol_tables(self.context, array.context)
            self.context = ast.create_context(
                ast=ast.Node(moa_operation, None, (), (left_context.ast, right_context.ast)),
                symbol_table=new_symbol_table)

        elif isinstance(left, (int, float, str)):
            self.context = ast.Node(moa_operation, None, (), (
                self.context.ast,
                self._create_array_from_int_float_string(array)))
        else:
            raise TypeError(f'not known how to handle outer product with type {type(array)}')
        return self

    def inner(self, left_operation, right_operation, array):
        if left_operation not in self.OPPERATION_MAP:
            raise ValueError(f'left operation {operation} not one of allowed operations {self.OPPERATION_MAP.keys()}')

        if right_operation not in self.OPPERATION_MAP:
            raise ValueError(f'right operation {operation} not one of allowed operations {self.OPPERATION_MAP.keys()}')

        moa_operation = (ast.NodeSymbol.DOT, self.OPPERATION_MAP[left_operation], self.OPPERATION_MAP[right_operation])

        if isinstance(array, self.__class__):
            new_symbol_table, left_context, right_context = ast.join_symbol_tables(self.context, array.context)
            self.context = ast.create_context(
                ast=ast.Node(moa_operation, None, (), (left_context.ast, right_context.ast)),
                symbol_table=new_symbol_table)
        else:
            raise TypeError(f'not known how to handle outer product with type {type(array)}')
        return self

    def reduce(self, operation):
        if operation not in self.OPPERATION_MAP:
            raise ValueError(f'operation {operation} not one of allowed operations {self.OPPERATION_MAP.keys()}')

        moa_operation = (ast.NodeSymbol.REDUCE, self.OPPERATION_MAP[operation])

        self.context = ast.create_context(
            ast=ast.Node(moa_operation, None, (), (self.context.ast,)),
            symbol_table=self.context.symbol_table)
        return self

    def _rbinary_opperation(self, operation, left):
        if isinstance(left, self.__class__):
            new_symbol_table, left_context, right_context = ast.join_symbol_tables(left.context, self.context)
            self.context = ast.create_context(
                ast=ast.Node((operation,), None, (), (left_context.ast, right_context.ast)),
                symbol_table=new_symbol_table)
        elif isinstance(left, (int, float, str)):
            self.context = ast.create_context(
                ast=ast.Node((operation,), None, (), (self._create_array_from_int_float_string(left), self.context.ast)),
                symbol_table=self.context.symbol_table)
        else:
            raise TypeError(f'not known how to handle binary operation with type {type(left)}')
        return self

    def _binary_opperation(self, operation, right):
        if isinstance(right, self.__class__):
            new_symbol_table, left_context, right_context = ast.join_symbol_tables(self.context, right.context)
            self.context = ast.create_context(
                ast=ast.Node((operation,), None, (), (left_context.ast, right_context.ast)),
                symbol_table=new_symbol_table)
        elif isinstance(right, (int, float, str)):
            self.context = ast.create_context(
                ast=ast.Node((operation,), None, (), (self.context.ast, self._create_array_from_int_float_string(right))),
                symbol_table=self.context.symbol_table)
        else:
            raise TypeError(f'not known how to handle binary operation with type {type(right)}')
        return self

    def __add__(self, other):
        return self._binary_opperation(ast.NodeSymbol.PLUS, other)

    def __radd__(self, other):
        return self._rbinary_opperation(ast.NodeSymbol.PLUS, other)

    def __sub__(self, other):
        return self._binary_opperation(ast.NodeSymbol.MINUS, other)

    def __rsub__(self, other):
        return self._rbinary_opperation(ast.NodeSymbol.MINUS, other)

    def __mul__(self, other):
        return self._binary_opperation(ast.NodeSymbol.TIMES, other)

    def __rmul__(self, other):
        return self._rbinary_opperation(ast.NodeSymbol.TIMES, other)

    def __truediv__(self, other):
        return self._binary_opperation(ast.NodeSymbol.DIVIDE, other)

    def __rtruediv__(self, other):
        return self._rbinary_opperation(ast.NodeSymbol.DIVIDE, other)

    def compile(self, backend='python', **kwargs):
        return compiler.compiler(self, frontend='array', backend=backend, **kwargs)

    def _shape(self):
        return calculate_shapes(self.context)

    def _dnf(self):
        return reduce_to_dnf(self._shape())

    def _onf(self):
        return reduce_to_onf(self._dnf())

    def analysis(self):
        shape_context = calculate_shapes(self.context)
        dnf_context = reduce_to_dnf(shape_context)

        return {
            'unoptimized_flops': metric_flops(shape_context),
            'optimized_flops': metric_flops(dnf_context)
        }

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
            dot = self.visualize()
            return dot.pipe(format='svg').decode(dot._encoding)
        except ImportError as e:
            return None
