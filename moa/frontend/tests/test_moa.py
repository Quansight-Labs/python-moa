import pytest

from ..moa import MOALexer, MOAParser


@pytest.mark.parametrize("expression,result", [
    ('1234', ('INTEGER',)),
    ('A', ('IDENTIFIER',)), ('asdf_asAVA', ['IDENTIFIER']),
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
    ('rav', ('RAV',))
    ('(', ('LPAREN',)), (')', ('RPAREN',)),
    ('<', ('LANGLEBRACKET',)), ('>', ('RANGLEBRACKET',)),
    ('^', ('CARROT',)),
])
def test_valid_single_token(expression, result):
    lexer = MOALexer()
    lexer.input(expression)
    tokens = [token.type for token in lexer]
    assert tokens == result
