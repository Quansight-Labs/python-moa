"""Utilities to help with testing moa

"""
import copy

from . import ast, visualize


def assert_transformation(tree, symbol_table, expected_tree, expected_symbol_table, operation, debug=False):
    context = ast.create_context(ast=tree, symbol_table=symbol_table)
    expected_context = ast.create_context(ast=expected_tree, symbol_table=expected_symbol_table)

    if debug:
        visualize.print_ast(context)
        visualize.print_ast(expected_context)
    assert_context_transformation(context, expected_context, operation)


def assert_context_transformation(context, expected_context, operation):
    context_copy = copy.deepcopy(context)

    new_context = operation(context)

    assert_context_equal(context, context_copy)
    assert_context_equal(new_context, expected_context)


def assert_context_equal(left_context, right_context):
    assert_ast_equal(left_context.ast, right_context.ast)
    assert_symbol_table_equal(left_context.symbol_table, right_context.symbol_table)


def assert_ast_equal(left_ast, right_ast, index=()):
    if left_ast.symbol != right_ast.symbol:
        raise ValueError(f'symbol {left_ast.symbol} != {right_ast.symbol} at node path {index}')

    if left_ast.shape != right_ast.shape:
        raise ValueError(f'shape {left_ast.shape} != {right_ast.shape} at node path {index}')

    if left_ast.attrib != right_ast.attrib:
        raise ValueError(f'attrib {left_ast.attrib} != {right_ast.attrib} at node path {index}')

    if len(left_ast.child) != len(right_ast.child):
        raise ValueError(f'left and right node have differing number of children {len(left_ast.child)} != {len(right_ast.child)} at node path {index}')

    for i, (left_child, right_child) in enumerate(zip(left_ast.child, right_ast.child)):
        assert_ast_equal(left_child, right_child, index + (i,))


def assert_symbol_table_equal(left_symbol_table, right_symbol_table):
    if left_symbol_table.keys() != right_symbol_table.keys():
        raise ValueError(f'left symbol table is missing keys {left_symbol_table.keys() - right_symbol_table.keys()} and right is missing keys {right_symbol_table.keys() - left_symbol_table.keys()}')

    for key in left_symbol_table:
        for attr in {'symbol', 'shape', 'type', 'value'}:
            left_value = getattr(left_symbol_table[key], attr)
            right_value = getattr(right_symbol_table[key], attr)
            if left_value != right_value:
                raise ValueError(f'left and right symbol nodes at "{key}.{attr}" do not match {left_value} != {right_value}')
