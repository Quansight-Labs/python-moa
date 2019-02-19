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


@pytest.mark.parametrize("expression,result", [
    ('<1 2 3> psi A',
     (MOANodeTypes.PSI, None,
      (MOANodeTypes.ARRAY, (3,), None, (1, 2, 3)),
      (MOANodeTypes.ARRAY, None, 'A', None))),
    ('<1 2 3> cat A ^ <3 5 7 9>',
     (MOANodeTypes.CAT, None,
      (MOANodeTypes.ARRAY, (3,), None, (1, 2, 3)),
      (MOANodeTypes.ARRAY, (3, 5, 7, 9), 'A',  None))),
    ('<0> psi ( tran (A + B))',
     (MOANodeTypes.PSI, None,
      (MOANodeTypes.ARRAY, (1,), None, (0,)),
      (MOANodeTypes.TRANSPOSE, None,
       (MOANodeTypes.PLUS, None,
        (MOANodeTypes.ARRAY, None, 'A', None),
        (MOANodeTypes.ARRAY, None, 'B', None))))),
    ('+red A ^ <3 4 5>',
     (MOANodeTypes.PLUSRED, None,
      (MOANodeTypes.ARRAY, (3, 4, 5), 'A', None))),
    # Lenore Simple Example #1 06/01/2018
    ('<0> psi ( tran (A^<3 4> + B^<3 4>))',
     (MOANodeTypes.PSI, None,
      (MOANodeTypes.ARRAY, (1,), None, (0,)),
      (MOANodeTypes.TRANSPOSE, None,
       (MOANodeTypes.PLUS, None,
        (MOANodeTypes.ARRAY, (3, 4), 'A', None),
        (MOANodeTypes.ARRAY, (3, 4), 'B', None)))))
])
def test_parser_simple_expressions(expression, result):
    parser = MOAParser()
    tree = parser.parse(expression)
    assert tree == result
