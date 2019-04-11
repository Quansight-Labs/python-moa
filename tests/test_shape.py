import copy

import pytest

from moa import ast, shape, testing


def test_dimension_array():
    symbol_table = {'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (3,))}
    node = ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ())
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    assert shape.dimension(context) == 0


def test_dimension_operation():
    symbol_table = {'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4), None, None)}
    node = ast.Node((ast.NodeSymbol.TRANSPOSE,), (4, 3), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (3, 4), ('_a1',), ()),))
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    assert shape.dimension(context) == 2


def test_is_scalar():
    symbol_table = {'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (3,))}
    node = ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ())
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    assert shape.is_scalar(context)


def test_is_not_scalar_1d(): # vector
    symbol_table = {'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (1, 2))}
    node = ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ())
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    assert not shape.is_scalar(context)


def test_is_not_scalar_2d(): # 2D array
    symbol_table = {'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2, 3), None, (1, 2, 3, 4, 5, 6))}
    node = ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ())
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    assert not shape.is_scalar(context)


def test_is_vector():
    symbol_table = {'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (5,), None, (1, 2, 3, 4, 5))}
    node = ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ())
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    assert shape.is_vector(context)


def test_is_not_vector_1d(): # scalar
    symbol_table = {'asdf': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (3,))}
    node = ast.Node((ast.NodeSymbol.ARRAY,), None, ('asdf',), ())
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    assert not shape.is_vector(context)


def test_is_not_vector_2d(): # 2D array
    symbol_table = {'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (5, 1), None, (1, 2, 3, 4, 5))}
    node = ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ())
    context = ast.create_context(ast=node, symbol_table=symbol_table)

    assert not shape.is_vector(context)




@pytest.mark.parametrize("symbol_table, tree, shape_symbol_table, shape_tree", [
    # ARRAY
    ({'A': ast.SymbolNode((ast.NodeSymbol.ARRAY,), (2,), None, (3, 5))},
     ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
     {'A': ast.SymbolNode((ast.NodeSymbol.ARRAY,), (2,), None, (3, 5))},
     ast.Node((ast.NodeSymbol.ARRAY,), (2,), ('A',), ())),
    # TRANSPOSE
    ({'_a0': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None)},
     ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a0',), ()),)),
     {'_a0': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None)},
     ast.Node((ast.NodeSymbol.TRANSPOSE,), (5, 4, 3), (), (
         ast.Node((ast.NodeSymbol.ARRAY,), (3, 4, 5), ('_a0',), ()),))),
    # TRANSPOSE VECTOR
    ({'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3,), None, (2, 0, 1)),
      'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None)},
     ast.Node((ast.NodeSymbol.TRANSPOSEV,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ()),)),
     {'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3,), None, (2, 0, 1)),
      'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None)},
     ast.Node((ast.NodeSymbol.TRANSPOSEV,), (4, 5, 3), (), (
         ast.Node((ast.NodeSymbol.ARRAY,), (3,), ('_a1',), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), (3, 4, 5), ('B',), ()),))),
    # ASSIGN
    ({'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None),
      'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None)},
     ast.Node((ast.NodeSymbol.ASSIGN,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ()),)),
     {'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None),
      'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None)},
     ast.Node((ast.NodeSymbol.ASSIGN,), (3, 4, 5), (), (
         ast.Node((ast.NodeSymbol.ARRAY,), (3, 4, 5), ('_a1',), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), (3, 4, 5), ('B',), ()),))),
    # SHAPE
    ({'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 2, 1), None, None)},
     ast.Node((ast.NodeSymbol.SHAPE,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), (3, 2, 1), ('_a1',), ()),)),
     {'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 2, 1), None, None)},
     ast.Node((ast.NodeSymbol.SHAPE,), (3,), (), (
         ast.Node((ast.NodeSymbol.ARRAY,), (3, 2, 1), ('_a1',), ()),))),
    # PSI
    ({'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (3, 4)),
      'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4, 5, 6), None, None)},
     ast.Node((ast.NodeSymbol.PSI,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),)),
     {'_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (3, 4)),
      'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4, 5, 6), None, None)},
     ast.Node((ast.NodeSymbol.PSI,), (6,), (), (
         ast.Node((ast.NodeSymbol.ARRAY,), (2,), ('_a1',), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), (4, 5, 6), ('A',), ()),))),
])
def test_shape_unit(symbol_table, tree, shape_symbol_table, shape_tree):
    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    expected_context = ast.create_context(ast=shape_tree, symbol_table=shape_symbol_table)
    context_copy = copy.deepcopy(context)
    new_context = shape.calculate_shapes(context)
    testing.assert_context_equal(context, context_copy)
    testing.assert_context_equal(new_context, expected_context)


@pytest.mark.parametrize("operation", [
    ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS,
    ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES,
])
def test_shape_unit_outer_plus_minus_multiply_divide_no_symbol(operation):
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3), None, None),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (4, 5, 6), None, None)
    }
    tree = ast.Node((ast.NodeSymbol.DOT, operation), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ()),))

    expected_tree = ast.Node((ast.NodeSymbol.DOT, operation), (1, 2, 3, 4, 5, 6), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3), ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), (4, 5, 6), ('B',), ()),))

    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    expected_context = ast.create_context(ast=expected_tree, symbol_table=symbol_table)
    context_copy = copy.deepcopy(context)

    new_context = shape.calculate_shapes(context)
    testing.assert_context_equal(context, context_copy)
    testing.assert_context_equal(expected_context, new_context)


@pytest.mark.parametrize("operation", [
    (ast.NodeSymbol.PLUS,  ast.NodeSymbol.PLUS),
    (ast.NodeSymbol.MINUS, ast.NodeSymbol.PLUS),
    (ast.NodeSymbol.DIVIDE,ast.NodeSymbol.PLUS),
    (ast.NodeSymbol.TIMES, ast.NodeSymbol.PLUS),
    (ast.NodeSymbol.PLUS,  ast.NodeSymbol.MINUS),
    (ast.NodeSymbol.MINUS, ast.NodeSymbol.MINUS),
    (ast.NodeSymbol.DIVIDE,ast.NodeSymbol.MINUS),
    (ast.NodeSymbol.TIMES, ast.NodeSymbol.MINUS),
    (ast.NodeSymbol.PLUS,  ast.NodeSymbol.TIMES),
    (ast.NodeSymbol.MINUS, ast.NodeSymbol.TIMES),
    (ast.NodeSymbol.DIVIDE,ast.NodeSymbol.TIMES),
    (ast.NodeSymbol.TIMES, ast.NodeSymbol.TIMES),
    (ast.NodeSymbol.PLUS,  ast.NodeSymbol.DIVIDE),
    (ast.NodeSymbol.MINUS, ast.NodeSymbol.DIVIDE),
    (ast.NodeSymbol.DIVIDE,ast.NodeSymbol.DIVIDE),
    (ast.NodeSymbol.TIMES, ast.NodeSymbol.DIVIDE),
])
def test_shape_unit_inner_plus_minus_multiply_divide_no_symbol(operation):
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3), None, None),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None)
    }
    tree = ast.Node((ast.NodeSymbol.DOT, *operation), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ()),))

    expected_tree = ast.Node((ast.NodeSymbol.DOT, *operation), (1, 2, 4, 5), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3), ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), (3, 4, 5), ('B',), ()),))

    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    expected_context = ast.create_context(ast=expected_tree, symbol_table=symbol_table)
    context_copy = copy.deepcopy(context)

    new_context = shape.calculate_shapes(context)
    testing.assert_context_equal(context, context_copy)
    testing.assert_context_equal(expected_context, new_context)


@pytest.mark.parametrize("operation", [
    ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS,
    ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES,
])
def test_shape_unit_reduce_plus_minus_multiply_divide_no_symbol(operation):
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, 3), None, None),
    }
    tree = ast.Node((ast.NodeSymbol.REDUCE, operation), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),))
    expected_tree = ast.Node((ast.NodeSymbol.REDUCE, operation), (2, 3), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (1, 2, 3), ('A',), ()),))
    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    expected_context = ast.create_context(ast=expected_tree, symbol_table=symbol_table)
    context_copy = copy.deepcopy(context)

    new_context = shape.calculate_shapes(context)
    testing.assert_context_equal(context, context_copy)
    testing.assert_context_equal(expected_context, new_context)


@pytest.mark.parametrize("operation", [
    ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS,
    ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES,
])
def test_shape_unit_plus_minus_multiply_divide_no_symbol(operation):
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None)
    }
    tree = ast.Node((operation,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ()),))
    expected_tree = ast.Node((operation,), (3, 4, 5), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (3, 4, 5), ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), (3, 4, 5), ('B',), ()),))

    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    expected_context = ast.create_context(ast=expected_tree, symbol_table=symbol_table)
    context_copy = copy.deepcopy(context)

    new_context = shape.calculate_shapes(context)
    testing.assert_context_equal(context, context_copy)
    testing.assert_context_equal(expected_context, new_context)


@pytest.mark.parametrize("operation", [
    ast.NodeSymbol.PLUS, ast.NodeSymbol.MINUS,
    ast.NodeSymbol.DIVIDE, ast.NodeSymbol.TIMES,
])
def test_shape_scalar_plus_minus_multiply_divide_no_symbol(operation):
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4, 5), None, None),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (0,))
    }
    tree = ast.Node((operation,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ()),))
    expected_tree = ast.Node((operation,), (3, 4, 5), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), (3, 4, 5), ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), (), ('B',), ()),))

    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    expected_context = ast.create_context(ast=expected_tree, symbol_table=symbol_table)
    context_copy = copy.deepcopy(context)

    new_context = shape.calculate_shapes(context)
    testing.assert_context_equal(context, context_copy)
    testing.assert_context_equal(expected_context, new_context)


@pytest.mark.parametrize("left_shape, right_shape", [
    ((3, 4, ast.Node((ast.NodeSymbol.ARRAY,), (), ('n',), ())), (3, 4, 5)),
    ((3, 4, 5), (3, 4, ast.Node((ast.NodeSymbol.ARRAY,), (), ('n',), ())))
])
def test_shape_unit_plus_symbolic(left_shape, right_shape):
    symbol_table = {
        'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, left_shape, None, None),
        'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, right_shape, None, None),
        'n': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, None),
    }
    tree = ast.Node((ast.NodeSymbol.PLUS,), None, (), (
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ()),))
    expected_tree = ast.Node((ast.NodeSymbol.PLUS,), (3, 4, 5), (), (
        ast.Node((ast.NodeSymbol.ARRAY,), left_shape, ('A',), ()),
        ast.Node((ast.NodeSymbol.ARRAY,), right_shape, ('B',), ()),))

    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    expected_context = ast.create_context(ast=expected_tree, symbol_table={
        **symbol_table,
        '_a3': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, (5,)),
    })
    context_copy = copy.deepcopy(context)

    new_context = shape.calculate_shapes(context)
    exclude_condition_node = ast.select_node(new_context, (1,))
    print(new_context.symbol_table)
    testing.assert_context_equal(context, context_copy)
    testing.assert_context_equal(expected_context, exclude_condition_node)
