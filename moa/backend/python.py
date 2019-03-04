import ast

from ..ast import MOANodeTypes, postorder_replacement


def python_backend(symbol_table, tree):
    symbol_table, python_ast = postorder_replacement(symbol_table, tree, _ast_replacement)
    return python_ast


def _ast_replacement(symbol_table, node):
    _NODE_AST_MAP = {
        MOANodeTypes.ARRAY: _ast_array,
        MOANodeTypes.PSI: _ast_psi,
        MOANodeTypes.PLUS: _ast_plus_minus_times_divide,
        MOANodeTypes.MINUS: _ast_plus_minus_times_divide,
        MOANodeTypes.TIMES: _ast_plus_minus_times_divide,
        MOANodeTypes.DIVIDE: _ast_plus_minus_times_divide,
        MOANodeTypes.EQUAL: _ast_comparison_operations,
        MOANodeTypes.NOTEQUAL: _ast_comparison_operations,
        MOANodeTypes.LESSTHAN: _ast_comparison_operations,
        MOANodeTypes.LESSTHANEQUAL: _ast_comparison_operations,
        MOANodeTypes.GREATERTHAN: _ast_comparison_operations,
        MOANodeTypes.GREATERTHANEQUAL: _ast_comparison_operations,
        MOANodeTypes.AND: _ast_boolean_operations,
        MOANodeTypes.OR: _ast_boolean_operations,
    }
    return _NODE_AST_MAP[node.node_type](symbol_table, node)


def _ast_psi(symbol_table, node):
    left_symbol_node = node.left_node.id
    indicies = [ast.Str(i) if isinstance(i, str) else ast.Num(i) for i in symbol_table[left_symbol_node].value]
    return symbol_table, ast.Subscript(value=node.right_node,
                                       slice=ast.Index(value=ast.Tuple(elts=indicies, ctx=ast.Load())),
                                       ctx=ast.Load())


def _ast_array(symbol_table, node):
    return symbol_table, ast.Name(id=node.symbol_node, ctx=ast.Load())


def _ast_plus_minus_times_divide(symbol_table, node):
    binop_map = {
        MOANodeTypes.PLUS: ast.Add,
        MOANodeTypes.MINUS: ast.Sub,
        MOANodeTypes.TIMES: ast.Mult,
        MOANodeTypes.DIVIDE: ast.Div,
    }
    return symbol_table, ast.BinOp(left=node.left_node, op=binop_map[node.node_type](), right=node.right_node)


def _ast_comparison_operations(symbol_table, node):
    comparision_map = {
        MOANodeTypes.EQUAL: ast.Eq,
        MOANodeTypes.NOTEQUAL: ast.NotEq,
        MOANodeTypes.LESSTHAN: ast.Lt,
        MOANodeTypes.LESSTHANEQUAL: ast.LtE,
        MOANodeTypes.GREATERTHAN: ast.Gt,
        MOANodeTypes.GREATERTHANEQUAL: ast.GtE,
    }
    return symbol_table, ast.Compare(left=node.left_node,
                                     ops=[comparision_map[node.node_type]()],
                                     comparators=[node.right_node])


def _ast_boolean_operations(symbol_table, node):
    boolean_map = {
        MOANodeTypes.AND: ast.And,
        MOANodeTypes.OR: ast.Or
    }
    return symbol_table, ast.BoolOp(op=boolean_map[node.node_type](), values=[node.left_node, node.right_node])
