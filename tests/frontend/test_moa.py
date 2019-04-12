import pytest

sly = pytest.importorskip('sly')

from moa.frontend.moa import MOALexer, MOAParser
from moa.exception import MOAException
from moa import testing
from moa import ast


@pytest.mark.parametrize("expression,result", [
    ('1234', ('INTEGER',)),
    ('A', ('IDENTIFIER',)),
    ('asdf_asAVA', ('IDENTIFIER',)),
    ('+', ('PLUS',)),
    ('-', ('MINUS',)),
    ('*', ('TIMES',)),
    ('/', ('DIVIDE',)),
    ('psi', ('PSI',)),
    ('take', ('TAKE',)),
    ('drop', ('DROP',)),
    ('cat', ('CAT',)),
    ('iota', ('IOTA',)),
    ('dim', ('DIM',)),
    ('tau', ('TAU',)),
    ('shp', ('SHAPE',)),
    ('rav', ('RAV',)),
    ('tran', ('TRANSPOSE',)),
    ('(', ('LPAREN',)),
    (')', ('RPAREN',)),
    ('<', ('LANGLEBRACKET',)),
    ('>', ('RANGLEBRACKET',)),
    ('^', ('CARROT',)),
])
def test_lexer_single_token(expression, result):
    lexer = MOALexer()
    tokens = tuple(token.type for token in lexer.tokenize(expression))
    assert tokens == result


@pytest.mark.parametrize("expression,symbol_table,tree", [
    # symbolic vector
    ('<1 b> psi A ^ <1 2 a>',
     {'a': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, None),
      'b': ast.SymbolNode(ast.NodeSymbol.ARRAY, (), None, None),
      '_a1': ast.SymbolNode(ast.NodeSymbol.ARRAY, (2,), None, (1, ast.Node((ast.NodeSymbol.ARRAY,), (), ('b',), ()))),
      'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1, 2, ast.Node((ast.NodeSymbol.ARRAY,), (), ('a',), ())), None, None)},
     ast.Node((ast.NodeSymbol.PSI,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a1',), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),))),
    # binary transpose
    ('<3 1 2> tran A',
     {'_a0': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3,), None, (3, 1, 2)),
      'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, None, None, None)},
     ast.Node((ast.NodeSymbol.TRANSPOSEV,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a0',), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),))),
    # indexing
    ('<1 2 3> psi A',
     {'_a0': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3,), None, (1, 2, 3)),
      'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, None, None, None)},
     ast.Node((ast.NodeSymbol.PSI,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a0',), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),))),
    ('<1 2 3> cat A ^ <3 5 7 9>',
     {'_a0': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3,), None, (1, 2, 3)),
      'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 5, 7, 9), None, None)},
     ast.Node((ast.NodeSymbol.CAT,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a0',), ()),
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),))),
    ('<0> psi ( tran (A + B))',
     {'_a0': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1,), None, (0,)),
      'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, None, None, None),
      'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, None, None, None)},
     ast.Node((ast.NodeSymbol.PSI,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a0',), ()),
         ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
             ast.Node((ast.NodeSymbol.PLUS,), None, (), (
                 ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
                 ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ()),)),)),))),
    # Lenore Simple Example #1 06/01/2018
    ('<0> psi ( tran (A^<3 4> + B^<3 4>))',
     {'_a0': ast.SymbolNode(ast.NodeSymbol.ARRAY, (1,), None, (0,)),
      'A': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4), None, None),
      'B': ast.SymbolNode(ast.NodeSymbol.ARRAY, (3, 4), None, None)},
     ast.Node((ast.NodeSymbol.PSI,), None, (), (
         ast.Node((ast.NodeSymbol.ARRAY,), None, ('_a0',), ()),
         ast.Node((ast.NodeSymbol.TRANSPOSE,), None, (), (
             ast.Node((ast.NodeSymbol.PLUS,), None, (), (
                 ast.Node((ast.NodeSymbol.ARRAY,), None, ('A',), ()),
                 ast.Node((ast.NodeSymbol.ARRAY,), None, ('B',), ()),)),)),))),
])
def test_parser_simple_expressions(expression, symbol_table, tree):
    parser = MOAParser()
    expected_context = ast.create_context(ast=tree, symbol_table=symbol_table)

    testing.assert_context_equal(parser.parse(expression), expected_context)


def test_parser_shape_mismatch_declaration():
    parser = MOAParser()
    expression = 'A ^ <2 3> + A ^ <2 3 4>'
    with pytest.raises(MOAException):
        parser.parse(expression)
