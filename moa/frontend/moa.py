"""Parse Matematics of Arrays (MOA) Expression to internal ast representation

"""

import sly
from sly.lex import LexError
from sly.yacc import YaccError

from ..ast import MOANodeTypes, ArrayNode, UnaryNode, BinaryNode


class MOALexer(sly.Lexer):
    tokens = {
        PLUS, MINUS, TIMES, DIVIDE,
        PSI, TAKE, DROP, CAT,
        PLUSRED, MINUSRED, TIMESRED, DIVIDERED,
        IOTA, DIM, TAU, SHAPE, RAV, TRANSPOSE,
        LANGLEBRACKET, RANGLEBRACKET,
        LPAREN, RPAREN,
        CARROT,
        INTEGER, IDENTIFIER
    }

    ignore = ' \t'

    @_(r'\n+')
    def newline(self, t):
        t.lineno += len(t.value)
        pass

    def comment(self, t):
        pass # skip comments

    @_(r'[+-]?\d+')
    def INTEGER(self, t):
        t.value = int(t.value)
        return t

    IDENTIFIER = r'[a-zA-Z][a-zA-Z0-9_]*'

    ## containers
    LPAREN = r'\('
    RPAREN = r'\)'
    LANGLEBRACKET = r'<'
    RANGLEBRACKET = r'>'
    CARROT = r'\^'

    ## unary operators
    PLUSRED   = r'\+red'
    MINUSRED  = r'\-red'
    TIMESRED  = r'\*red'
    DIVIDERED = r'/red'
    IDENTIFIER['iota'] = IOTA
    IDENTIFIER['dim']  = DIM
    IDENTIFIER['shp']  = SHAPE
    IDENTIFIER['tau']  = TAU
    IDENTIFIER['rav']  = RAV
    IDENTIFIER['tran'] = TRANSPOSE

    ## binary operators
    PLUS   = r'\+'
    MINUS  = r'\-'
    TIMES  = r'\*'
    DIVIDE = r'/'
    IDENTIFIER['psi'] = PSI
    IDENTIFIER['take'] = TAKE
    IDENTIFIER['drop'] = DROP
    IDENTIFIER['cat'] = CAT

    def error(self, t):
        raise ValueError(f"Illegal character '{t.value[0]}' no valid token can be formed from '{t.value}' on line {t.lexer.lineno}")


class MOAParser(sly.Parser):
    tokens = MOALexer.tokens

    precedence = (
        ('left', 'PSI', 'TAKE', 'DROP', 'CAT'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('right', 'IOTA', 'DIM', 'TAU', 'SHAPE', 'RAV', 'PLUSRED', 'MINUSRED', 'TIMESRED', 'DIVIDERED')
    )

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('IOTA expr',
       'DIM expr',
       'TAU expr',
       'SHAPE expr',
       'RAV expr',
       'TRANSPOSE expr',
       'PLUSRED expr',
       'MINUSRED expr',
       'TIMESRED expr',
       'DIVIDERED expr')
    def expr(self, p):
        unary_map = {
            '+red': MOANodeTypes.PLUSRED,
            '-red': MOANodeTypes.MINUSRED,
            '*red': MOANodeTypes.TIMESRED,
            '/red': MOANodeTypes.DIVIDERED,
            'tran': MOANodeTypes.TRANSPOSE,
            'iota': MOANodeTypes.IOTA,
            'dim': MOANodeTypes.DIM,
            'tau': MOANodeTypes.TAU,
            'shp': MOANodeTypes.SHAPE,
            'rav': MOANodeTypes.RAV,
        }
        return UnaryNode(unary_map[p[0].lower()], None, p.expr)

    @_('expr PLUS   expr',
       'expr MINUS  expr',
       'expr TIMES  expr',
       'expr DIVIDE expr',
       'expr PSI    expr',
       'expr TAKE   expr',
       'expr DROP   expr',
       'expr CAT    expr'
    )
    def expr(self, p):
        binary_map = {
            '+': MOANodeTypes.PLUS,
            '-': MOANodeTypes.MINUS,
            '*': MOANodeTypes.TIMES,
            '/': MOANodeTypes.DIVIDE,
            'psi': MOANodeTypes.PSI,
            'take': MOANodeTypes.TAKE,
            'drop': MOANodeTypes.DROP,
            'cat': MOANodeTypes.CAT,
        }
        return BinaryNode(binary_map[p[1].lower()], None, p.expr0, p.expr1)

    @_('array')
    def expr(self, p):
        return p.array

    @_('IDENTIFIER CARROT LANGLEBRACKET integer_list RANGLEBRACKET')
    def array(self, p):
        return ArrayNode(MOANodeTypes.ARRAY, tuple(p.integer_list), p.IDENTIFIER, None)

    @_('IDENTIFIER')
    def array(self, p):
        return ArrayNode(MOANodeTypes.ARRAY, None, p.IDENTIFIER, None)

    @_('LANGLEBRACKET integer_list RANGLEBRACKET')
    def array(self, p):
        return ArrayNode(MOANodeTypes.ARRAY, (len(p.integer_list),), None, tuple(p.integer_list))

    @_('INTEGER integer_list')
    def integer_list(self, p):
        return (p.INTEGER,) + p.integer_list

    @_('empty')
    def integer_list(self, p):
        return tuple()

    @_('')
    def empty(self, p):
        pass

    def error(self, p):
        if p:
            raise YaccError(f'Syntax error at line {p.lineno}, token={p.type}, value={p.value}\n')
        else:
            raise YaccError('Parse error in input. EOF\n')

    def parse(self, text):
        lexer = MOALexer()
        tokens = lexer.tokenize(text)
        tree = super().parse(tokens)
        return tree
