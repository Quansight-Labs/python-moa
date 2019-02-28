import pytest

from moa.frontend import MOALexer, MOAParser
from moa.ast import MOANodeTypes


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
    ('+red', ('PLUSRED',)),
    ('-red', ('MINUSRED',)),
    ('*red', ('TIMESRED',)),
    ('/red', ('DIVIDERED',)),
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
     {'a': (MOANodeTypes.INDEX, None),
      'b': (MOANodeTypes.INDEX, None),
      '_1': (MOANodeTypes.ARRAY, (2,), (1, 'b')),
      'A': (MOANodeTypes.ARRAY, (1, 2, 'a'), None)},
     (MOANodeTypes.PSI, None,
      (MOANodeTypes.ARRAY, None, '_1'),
      (MOANodeTypes.ARRAY, None, 'A'))),
    # binary transpose
    ('<3 1 2> tran A',
     {'_1': (MOANodeTypes.ARRAY, (3,), (3, 1, 2)),
      'A': (MOANodeTypes.ARRAY, None, None)},
     (MOANodeTypes.TRANSPOSEV, None,
      (MOANodeTypes.ARRAY, None, '_1'),
      (MOANodeTypes.ARRAY, None, 'A'))),
    # indexing
    ('<1 2 3> psi A',
     {'_1': (MOANodeTypes.ARRAY, (3,), (1, 2, 3)),
      'A': (MOANodeTypes.ARRAY, None, None)},
     (MOANodeTypes.PSI, None,
      (MOANodeTypes.ARRAY, None, '_1'),
      (MOANodeTypes.ARRAY, None, 'A'))),
    ('<1 2 3> cat A ^ <3 5 7 9>',
     {'_1': (MOANodeTypes.ARRAY, (3,), (1, 2, 3)),
      'A': (MOANodeTypes.ARRAY, (3, 5, 7, 9), None)},
     (MOANodeTypes.CAT, None,
      (MOANodeTypes.ARRAY, None, '_1'),
      (MOANodeTypes.ARRAY, None, 'A'))),
    ('<0> psi ( tran (A + B))',
     {'_1': (MOANodeTypes.ARRAY, (1,), (0,)),
      'A': (MOANodeTypes.ARRAY, None, None),
      'B': (MOANodeTypes.ARRAY, None, None)},
     (MOANodeTypes.PSI, None,
      (MOANodeTypes.ARRAY, None, '_1'),
      (MOANodeTypes.TRANSPOSE, None,
       (MOANodeTypes.PLUS, None,
        (MOANodeTypes.ARRAY, None, 'A'),
        (MOANodeTypes.ARRAY, None, 'B'))))),
    ('+red A ^ <3 4 5>',
     {'A': (MOANodeTypes.ARRAY, (3, 4, 5), None)},
     (MOANodeTypes.PLUSRED, None,
      (MOANodeTypes.ARRAY, None, 'A'))),
    # Lenore Simple Example #1 06/01/2018
    ('<0> psi ( tran (A^<3 4> + B^<3 4>))',
     {'_1': (MOANodeTypes.ARRAY, (1,), (0,)),
      'A': (MOANodeTypes.ARRAY, (3, 4), None),
      'B': (MOANodeTypes.ARRAY, (3, 4), None)},
     (MOANodeTypes.PSI, None,
      (MOANodeTypes.ARRAY, None, '_1'),
      (MOANodeTypes.TRANSPOSE, None,
       (MOANodeTypes.PLUS, None,
        (MOANodeTypes.ARRAY, None, 'A'),
        (MOANodeTypes.ARRAY, None, 'B')))))
])
def test_parser_simple_expressions(expression, symbol_table, tree):
    parser = MOAParser()
    assert (symbol_table, tree) == parser.parse(expression)
