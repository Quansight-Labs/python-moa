"""Parse Matematics of Arrays (MOA) Expression to internal ast representation

"""

import sly
from sly.lex import LexError
from sly.yacc import YaccError

from .. import ast


class MOALexer(sly.Lexer):
    tokens = {
        PLUS, MINUS, TIMES, DIVIDE,
        PSI, TAKE, DROP, CAT,
        IOTA, DIM, TAU, SHAPE, RAV, TRANSPOSE,
        LANGLEBRACKET, RANGLEBRACKET,
        LPAREN, RPAREN,
        CARROT,
        INTEGER, IDENTIFIER
    }

    ignore = ' \t'

    @_(r'\n+')
    def newline(self, t):
        self.lineno += len(t.value)
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
        raise ValueError(f"Illegal character '{t.value[0]}' no valid token can be formed from '{t.value}' on line {self.lineno}")


class MOAParser(sly.Parser):
    tokens = MOALexer.tokens

    precedence = (
        ('right', 'UNARYOP'),
        ('left', 'BINARYOP'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
    )

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('unary_operation expr %prec UNARYOP')
    def expr(self, p):
        return ast.Node((p.unary_operation,), None, (), (p.expr,))

    @_('IOTA',
       'DIM',
       'TAU',
       'SHAPE',
       'RAV',
       'TRANSPOSE')
    def unary_operation(self, p):
        unary_map = {
            'tran': ast.NodeSymbol.TRANSPOSE,
            'iota': ast.NodeSymbol.IOTA,
            'dim': ast.NodeSymbol.DIM,
            'tau': ast.NodeSymbol.TAU,
            'shp': ast.NodeSymbol.SHAPE,
            'rav': ast.NodeSymbol.RAV,
        }
        return unary_map[p[0].lower()]

    @_('expr binary_operation expr %prec BINARYOP')
    def expr(self, p):
        return ast.Node((p.binary_operation,), None, (), (p.expr0, p.expr1))

    @_('PLUS',
       'MINUS',
       'TIMES',
       'DIVIDE',
       'PSI',
       'TAKE',
       'DROP',
       'CAT',
       'TRANSPOSE')
    def binary_operation(self, p):
        binary_map = {
            '+': ast.NodeSymbol.PLUS,
            '-': ast.NodeSymbol.MINUS,
            '*': ast.NodeSymbol.TIMES,
            '/': ast.NodeSymbol.DIVIDE,
            'psi': ast.NodeSymbol.PSI,
            'take': ast.NodeSymbol.TAKE,
            'drop': ast.NodeSymbol.DROP,
            'cat': ast.NodeSymbol.CAT,
            'tran': ast.NodeSymbol.TRANSPOSEV,
        }
        return binary_map[p[0].lower()]

    @_('array')
    def expr(self, p):
        return p.array

    @_('IDENTIFIER CARROT LANGLEBRACKET vector_list RANGLEBRACKET')
    def array(self, p):
        self.context = ast.add_symbol(self.context, p.IDENTIFIER, ast.NodeSymbol.ARRAY, tuple(p.vector_list), None, None)
        return ast.Node((ast.NodeSymbol.ARRAY,), None, (p.IDENTIFIER,), ())

    @_('IDENTIFIER')
    def array(self, p):
        self.context = ast.add_symbol(self.context, p.IDENTIFIER, ast.NodeSymbol.ARRAY, None, None, None)
        return ast.Node((ast.NodeSymbol.ARRAY,), None, (p.IDENTIFIER,), ())

    @_('LANGLEBRACKET vector_list RANGLEBRACKET')
    def array(self, p):
        unique_array_name = ast.generate_unique_array_name(self.context)
        self.context = ast.add_symbol(self.context, unique_array_name, ast.NodeSymbol.ARRAY, (len(p.vector_list),), None, tuple(p.vector_list))
        return ast.Node((ast.NodeSymbol.ARRAY,), None, (unique_array_name,), ())

    @_('INTEGER vector_list')
    def vector_list(self, p):
        return (p.INTEGER,) + p.vector_list

    @_('IDENTIFIER vector_list')
    def vector_list(self, p):
        self.context = ast.add_symbol(self.context, p.IDENTIFIER, ast.NodeSymbol.ARRAY, (), None, None)
        return (ast.Node((ast.NodeSymbol.ARRAY,), (), (p.IDENTIFIER,), ()),) + p.vector_list

    @_('empty')
    def vector_list(self, p):
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
        self.context = ast.create_context()

        lexer = MOALexer()
        tokens = lexer.tokenize(text)
        tree = super().parse(tokens)

        return ast.create_context(ast=tree, symbol_table=self.context.symbol_table)
