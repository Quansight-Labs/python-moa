from .moa import MOALexer, MOAParser


if __name__ == "__main__":
    lexer = MOALexer()
    parser = MOAParser()

    print('MOA Calculator')
    while True:
        text = input('>>> ')
        if text in {'q', 'quit'}: break
        print(parser.parse(lexer.tokenize(text)))
